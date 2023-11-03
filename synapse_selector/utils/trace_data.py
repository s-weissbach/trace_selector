import pandas as pd
from pandas.api.types import is_string_dtype
import numpy as np
import os

from synapse_selector.utils.fraction_respond_first_pulse import compute_fraction_first_pulse
from .ppr_calculation import paired_pulse_ratio
from .decay_compute import compute_tau
from .failure_rate import failure_rate


class synapse_response_data_class:
    def __init__(self,
                 filepath: str,
                 filename: str,
                 meta_columns: list[str]) -> None:
        self.filename = filename
        if filepath.endswith('.txt') or filepath.endswith('.csv'):
            self.df = pd.read_csv(filepath, sep=',')
        else:
            self.df = pd.read_excel(filepath)
        self.meta_columns = [col for col in self.df.columns if col in meta_columns or is_string_dtype(self.df[col])]
        self.columns = [col for col in self.df.columns if col not in self.meta_columns]
        self.keep_data = []
        self.trash_data = []
        self.idx = 0
        self.last = []
        self.peaks = []
        self.manual_peaks = []
        self.selected_peaks = []
        self.intensity = self.df[self.columns[self.idx]].to_numpy()
        self.time = np.arange(len(self.intensity))
        self.automatic_peaks = []

    def __len__(self) -> int:
        '''
        returns number of traces to look at as length.
        '''
        return len(self.columns)

    def return_state(self) -> str:
        '''
        returns index and length of current file and computes percentage of
        sorted traces.
        '''
        percentage = np.round(self.idx / len(self), 4)*100
        return f'{self.idx+1}/{len(self)} ({percentage}%)'

    def save(self,
             export_xlsx: bool,
             keep_path: str,
             trash_path: str,
             ppr: bool,
             stimulation_timepoints: list[int],
             patience: int) -> None:
        '''
        Save the sorted trace to the respective keep and trash file and if peak
        detection was used also save the result table for the keep responses.
        '''
        keep_df = self.df[self.meta_columns+self.keep_data]
        trash_df = self.df[self.meta_columns+self.trash_data]
        if export_xlsx:
            keep_df.to_excel(os.path.join(keep_path, f'{self.filename}.xlsx'), index=False)
            trash_df.to_excel(os.path.join(trash_path, f'{self.filename}.xlsx'), index=False)
        elif self.filename.endswith('.xlsx') or self.filename.endswith('.xls'):
            keep_df.to_excel(os.path.join(keep_path, f'{self.filename}.xlsx'), index=False)
            trash_df.to_excel(os.path.join(trash_path, f'{self.filename}.xlsx'), index=False)
        else:
            keep_df.to_csv(os.path.join(keep_path, self.filename), index=False)
            trash_df.to_csv(os.path.join(trash_path, self.filename), index=False)
        if len(self.selected_peaks) > 0:
            peak_df = pd.DataFrame(self.selected_peaks, columns=['Filename', 'ROI#', 'Frame', 'abs. Amplitude',
                                   'rel. Amplitude', 'decay constant (tau)', 'inv. decay constant (invtau)'])
            if export_xlsx:
                output_name = f"{'.'.join(self.filename.split('.')[:-1])}_responses.xlsx"
                peak_df.to_excel(os.path.join(keep_path, output_name), index=False)
            else:
                output_name = f"{'.'.join(self.filename.split('.')[:-1])}_responses.csv"
                peak_df.to_csv(os.path.join(keep_path, output_name), index=False)
            if ppr:
                ppr_df = paired_pulse_ratio(peak_df, stimulation_timepoints, patience)
                if export_xlsx:
                    output_name = f"{'.'.join(self.filename.split('.')[:-1])}_ppr.xlsx"
                    ppr_df.to_excel(os.path.join(keep_path, output_name), index=False)
                else:
                    output_name = f"{'.'.join(self.filename.split('.')[:-1])}_ppr.csv"
                    ppr_df.to_csv(os.path.join(keep_path, output_name), index=False)
            if len(stimulation_timepoints) > 0:
                # failure rate on a synaptic level
                failure_df = failure_rate(peak_df, stimulation_timepoints, patience)
                if export_xlsx:
                    output_name = f"{'.'.join(self.filename.split('.')[:-1])}_failurerate.xlsx"
                    failure_df.to_excel(os.path.join(keep_path, output_name), index=False)
                else:
                    output_name = f"{'.'.join(self.filename.split('.')[:-1])}_failurerate.csv"
                    failure_df.to_csv(os.path.join(keep_path, output_name), index=False)
                # fraction responding to the first pulse
                responses_first_pulse = compute_fraction_first_pulse(peak_df, stimulation_timepoints, patience)
                if export_xlsx:
                    output_name = f"{'.'.join(self.filename.split('.')[:-1])}_fraction_respond_first_pulse.xlsx"
                    responses_first_pulse.to_excel(os.path.join(keep_path, output_name), index=False)
                else:
                    output_name = f"{'.'.join(self.filename.split('.')[:-1])}_fraction_respond_first_pulse.csv"
                    responses_first_pulse.to_csv(os.path.join(keep_path, output_name), index=False)



    def next(self) -> None:
        '''
        Go to next trace and load the data
        '''
        self.idx += 1
        self.peaks = []
        self.manual_peaks = []
        self.intensity = self.df[self.columns[self.idx]].to_numpy()
        self.time = np.arange(len(self.intensity))

    def back(self) -> bool:
        '''
        Go back one trace and undo the selection. If it is the first trace of
        the file, nothing is done.
        '''
        if self.idx == 0:
            return False
        if self.last[-1] == 'keep':
            _ = self.keep_data.pop()
            _ = self.last.pop()
        else:
            _ = self.trash_data.pop()
            _ = self.last.pop()
        selected_peaks_copy = self.selected_peaks.copy()
        self.selected_peaks = []
        for peak in selected_peaks_copy:
            if peak[1] == self.columns[self.idx-1]:
                continue
            self.selected_peaks.append(peak)
        self.idx -= 2
        return True

    def keep(self,
             select_responses: bool,
             frames_for_decay: int,
             selection: list[int]) -> None:
        '''
        Puts currently viewed trace to the keep data and if peaks selected appends
        them to the selected_peaks.
        '''
        self.keep_data.append(self.columns[self.idx])
        self.last.append('keep')
        if not select_responses:
            return
        # -------------------------- save selected responses ------------------------- #
        for peak_tp in selection:
            amplitude = self.intensity[peak_tp]
            baseline = np.min(self.intensity[max(0, peak_tp-15):peak_tp])
            relative_height = amplitude-baseline
            pos_after_peak = min(peak_tp+frames_for_decay,len(self.intensity-1))
            inv_tau,tau = compute_tau(self.intensity[peak_tp:pos_after_peak])
            self.selected_peaks.append([
                self.filename,
                self.columns[self.idx],
                peak_tp,
                amplitude,
                relative_height,
                tau,
                inv_tau
            ])

    def trash(self) -> None:
        '''
        Puts currently viewed trace to trash.
        '''
        self.trash_data.append(self.columns[self.idx])
        self.last.append('trash')

    def trash_rest(self) -> None:
        '''
        Puts all remaining not seen traces to the trash df.
        '''
        self.trash_data += [self.columns[i] for i in range(self.idx, len(self.columns))]
        self.idx = len(self.columns)-1

    def end_of_file(self) -> bool:
        '''
        Checks whether a next trace can be loaded or end of file will be reached.
        '''
        if self.idx+1 == len(self):
            return True
        return False

    def add_automatic_peaks(self, peaks: list[int]) -> None:
        '''
        Add automatic peaks to peak list.
        '''
        self.automatic_peaks = peaks
        self.peaks = self.automatic_peaks + self.manual_peaks

    def add_manual_peak(self, peak: int) -> bool:
        '''
        Check if the manual peak is valid and if so add it to the peaks.
        '''
        if not (peak not in self.peaks and
                peak not in self.manual_peaks and
                peak >= 0 and peak < len(self.time)):
            return False
        self.manual_peaks.append(peak)
        self.peaks = self.automatic_peaks + self.manual_peaks
        return True

    def non_max_supression(self, 
                           stimframes: list[int],
                           patience: int) -> list[int]:
        '''
        Keeps only maximum peak per stimulation
        '''
        nms_peaks = []
        for stimframe in stimframes:
            tmp_peaks = []
            tmp_amplitudes = []
            for peak in self.automatic_peaks:
                if peak < stimframe or peak > stimframe + patience:
                    continue
                tmp_peaks.append(peak)
                tmp_amplitudes.append(self.intensity[peak])
            if len(tmp_peaks) > 1:
                _ = tmp_peaks.pop(np.argmax(tmp_amplitudes))
                for peak in tmp_peaks:
                    nms_peaks.append(peak)
        return nms_peaks
