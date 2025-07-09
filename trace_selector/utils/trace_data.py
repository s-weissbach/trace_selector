from typing import Literal
import pandas as pd
from pandas.api.types import is_string_dtype
import numpy as np
import os
from PyQt6.QtWidgets import QMessageBox
from io import StringIO
from pathlib import Path

from .post_selection.decay_compute import compute_tau
from .post_selection.failure_rate import failure_rate
from .normalization import sliding_window_normalization, baseline_normalization
from .export import (
    create_stimulation_df,
    create_peak_df,
    create_ppr_df,
    create_fraction_first_pulse_df,
    create_settings_df,
    write_excel_output,
    normalized_trace_df,
)


class SynapseResponseData:
    def __init__(self, parent) -> None:
        self.parent = parent

        self.df = pd.DataFrame()
        self.meta_columns = []
        self.columns = []
        self.keep_data = []
        self.discard_data = []
        self.idx = 0
        self.last = []
        self.peaks = []
        self.manual_peaks = []
        self.selected_peaks = []
        self.intensity = np.empty(0, dtype=np.float64)
        self.norm_intensity = np.empty(0, dtype=np.float64)
        self.time = np.empty(0, dtype=np.float64)
        self.automatic_peaks = []
        self.file_opened = False

    def open_file(
        self,
        path: Path,
        meta_columns: list[str],
        normalization_mode: Literal[10,11,12,13],
        normalization_sliding_window: int,
        normalization_baseline_window: tuple[int, int],
    ):
        self.path = path
        if path.suffix == ".virtual":
            self.df = pd.read_csv(StringIO(path), sep=",")
        elif path.suffix in [".txt", ".csv"]:
            self.df = pd.read_csv(path, sep=",")
        elif path.suffix in [".xlsx", "xls"]:
            self.df = pd.read_excel(path)
        else:
            msg = QMessageBox(self.parent)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Warning")
            msg.setText(
                f"Can't open the given file: Invalid file type"
            )
            msg.exec()
        # format all columns to str
        all_columns = [str(col) for col in self.df.columns]
        self.df.columns = all_columns
        self.meta_columns = [
            col
            for col in all_columns
            if col in meta_columns or is_string_dtype(self.df[col])
        ]
        self.columns = [col for col in all_columns if col not in self.meta_columns]

        self.keep_data = []
        self.discard_data = []
        self.idx = 0
        self.last = []
        self.peaks = []
        self.manual_peaks = []
        self.selected_peaks = []
        self.intensity = self.df[self.columns[self.idx]].to_numpy(dtype=np.float64)

        if normalization_mode == 11 or normalization_mode == 12:
            self.norm_intensity = sliding_window_normalization(
                self.df[self.columns[self.idx]].to_numpy(),
                True if (normalization_mode == 12) else False,
                normalization_sliding_window,
            )
        elif normalization_mode == 13:
            self.norm_intensity = baseline_normalization(
                self.df[self.columns[self.idx]].to_numpy(),
                normalization_baseline_window
            )
        else:
            self.norm_intensity = self.df[self.columns[self.idx]].to_numpy()
        self.time = np.arange(len(self.intensity))
        self.automatic_peaks = []
        self.file_opened = True

    def __len__(self) -> int:
        """
        returns number of traces to look at as length.
        """
        return len(self.columns)

    def return_state(self) -> str:
        """
        returns index and length of current file and computes percentage of
        sorted traces.
        """
        percentage = np.round(((self.idx + 1) / len(self)) * 100, 2)
        return f"{self.idx+1}/{len(self)} ({np.round(percentage,2)}%)"

    def save(self, stimulation_timepoints: list[int], settings: dict) -> None:
        """
        Save the sorted trace to the respective keep and discard file and if peak
        detection was used also save the result table for the keep responses.
        """
        keep_path = Path(settings["output_filepath"]) / "keep_folder"
        discard_path = Path(settings["output_filepath"]) / "discard_folder"
        export_xlsx = settings["export_xlsx"]
        ppr = settings["compute_ppr"]
        patience_l = settings["stim_frames_patience_l"]
        patience_r = settings["stim_frames_patience_r"]
        keep_path.mkdir(exist_ok=True)
        discard_path.mkdir(exist_ok=True)
        keep_df = self.df[self.meta_columns + self.keep_data]
        discard_df = self.df[self.meta_columns + self.discard_data]
        if settings["export_normalized_traces"]:
            normalized_keep_df = normalized_trace_df(
                keep_df[self.keep_data],
                settings["normalization_mode"],
                settings["normalization_sliding_window_size"],
                [int(x) for x in settings["normalization_baseline_window"].split(":")],
            )
            # instert meta_columns
            for i, col in enumerate(self.meta_columns):
                normalized_keep_df.insert(i, col, self.df[col])
        
        fname = self.path.stem
        suffix = ".csv"
        if (export_xlsx or suffix in [".xlsx", "xls"]):
            suffix = ".xlsx"
            
        if (keep_path / (fname+ suffix)).exists():
            for i in range(1, 10):
                if not (keep_path / ((new_fname := f"{fname} ({i})") + suffix)).exists():
                    fname = new_fname
                    break
            else:
                msg = QMessageBox(self.parent)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Warning")
                msg.setText(
                    f"The file {self.path.name} alreads exists in {keep_path}. Saved as {fname}.{suffix}"
                )
                msg.exec()

        if suffix == ".xlsx":
            keep_df.to_excel(keep_path / (fname + suffix), index=False)
            if settings["export_normalized_traces"]:
                normalized_keep_df.to_excel(keep_path / (fname + "_normalized" + suffix), index=False)
            discard_df.to_excel(discard_path / (fname + suffix), index=False)
        else:
            keep_df.to_csv(keep_path / (fname + suffix), index=False)
            if settings["export_normalized_traces"]:
                normalized_keep_df.to_csv(keep_path / (fname + "_normalized" + suffix), index=False)
            discard_df.to_csv(discard_path / (fname + suffix), index=False)

        analysis_dfs = []
        analysis_names = []
        settings_df = create_settings_df(settings)
        analysis_dfs.append(settings_df)
        analysis_names.append("parameters")
        if len(self.selected_peaks) > 0:
            peak_df = create_peak_df(self.selected_peaks)
            analysis_dfs.append(peak_df)
            analysis_names.append("responses")
            stimulation_df = create_stimulation_df(
                stimulation_timepoints, patience_l, patience_r, peak_df
            )
            analysis_dfs.append(stimulation_df)
            analysis_names.append("stimulations")
            if ppr:
                ppr_df = create_ppr_df(peak_df, stimulation_timepoints, patience_l, patience_r)
                analysis_dfs.append(ppr_df)
                analysis_names.append("PPR")
            if len(stimulation_timepoints) > 0:
                # failure rate on a synaptic level
                failure_df = failure_rate(peak_df, stimulation_timepoints, patience_l, patience_r, self.columns)
                analysis_dfs.append(failure_df)
                analysis_names.append("failure_analysis")
                # fraction responding to the first pulse
                responses_first_pulse_df = create_fraction_first_pulse_df(
                    peak_df, stimulation_timepoints, patience_l, patience_r
                )
                analysis_dfs.append(responses_first_pulse_df)
                analysis_names.append("responses_first_pulse")
        if len(analysis_dfs) > 0:
            write_excel_output(analysis_dfs, analysis_names, keep_path / (fname + "_analysis.xlsx"))

    def next(
        self, 
        normalization_mode: Literal[10,11,12,13], 
        normalization_sliding_window: int,
        normalization_baseline_window: tuple[int,int]
    ) -> None:
        """
        Go to next trace and load the data
        """
        self.idx += 1
        self.peaks = []
        self.manual_peaks = []
        self.intensity = self.df[self.columns[self.idx]].to_numpy()

        if normalization_mode == 11 or normalization_mode == 12:
            self.norm_intensity = sliding_window_normalization(
                self.df[self.columns[self.idx]].to_numpy(),
                True if (normalization_mode == 12) else False,
                normalization_sliding_window,
            )
        elif normalization_mode == 13:
            self.norm_intensity = baseline_normalization(
                self.df[self.columns[self.idx]].to_numpy(),
                normalization_baseline_window
            )
        else:
            self.norm_intensity = self.df[self.columns[self.idx]].to_numpy()
        self.time = np.arange(len(self.intensity))

    def back(self) -> bool:
        """
        Go back one trace and undo the selection. If it is the first trace of
        the file, nothing is done.
        """
        if self.idx == 0:
            return False
        if self.last[-1] == "keep":
            _ = self.keep_data.pop()
            _ = self.last.pop()
        else:
            _ = self.discard_data.pop()
            _ = self.last.pop()
        selected_peaks_copy = self.selected_peaks.copy()
        self.selected_peaks = []
        for peak in selected_peaks_copy:
            if peak[1] == self.columns[self.idx - 1]:
                continue
            self.selected_peaks.append(peak)
        self.idx -= 2
        return True

    def keep(
        self,
        select_responses: bool,
        frames_for_decay: int,
        peak_dict: dict,
        stimulation: list[int],
        patience_l: int,
        patience_r: int,
    ) -> None:
        """
        Puts currently viewed trace to the keep data and if peaks selected appends
        them to the selected_peaks.
        """
        self.keep_data.append(self.columns[self.idx])
        self.last.append("keep")
        if not select_responses:
            return
        # -------------------------- save selected responses ------------------------- #
        for peak_tp in [peak for peak, selected in peak_dict.items() if selected]:
            amplitude = self.intensity[peak_tp]
            baseline = np.median(self.intensity[max(0, peak_tp - 15) : peak_tp])
            relative_height = amplitude - baseline
            norm_amplitude = self.norm_intensity[peak_tp]
            norm_baseline = np.median(
                self.norm_intensity[max(0, peak_tp - 15) : peak_tp]
            )
            norm_rel_amplitude = norm_amplitude - norm_baseline
            pos_after_peak = min(peak_tp + frames_for_decay, len(self.intensity - 1))
            inv_tau, tau = compute_tau(self.intensity[peak_tp:pos_after_peak])
            automatic_detected = True if peak_tp in self.automatic_peaks else False
            responded_to_stim = np.array([True if peak_tp >= (stim - patience_l) and peak_tp <= (stim + patience_r) else False for stim in stimulation])
            
            evoked = np.any(responded_to_stim)
            self.selected_peaks.append(
                [
                    self.path.stem,
                    self.columns[self.idx],
                    peak_tp,
                    amplitude,
                    relative_height,
                    norm_amplitude,
                    norm_rel_amplitude,
                    evoked,
                    automatic_detected,
                    tau,
                    inv_tau,
                ]
            )

    def discard(self) -> None:
        """
        Discards currently viewed trace.
        """
        self.discard_data.append(self.columns[self.idx])
        self.last.append("trash")

    def discard_rest(self) -> None:
        """
        Discards all remaining not seen traces.
        """
        self.discard_data += [
            self.columns[i] for i in range(self.idx, len(self.columns))
        ]
        self.idx = len(self.columns) - 1

    def end_of_file(self) -> bool:
        """
        Checks whether a next trace can be loaded or end of file will be reached.
        """
        if self.idx + 1 == len(self):
            return True
        return False

    def add_automatic_peaks(self, peaks: list) -> None:
        """
        Add automatic peaks to peak list.
        """
        self.automatic_peaks = peaks
        self.peaks = self.automatic_peaks + self.manual_peaks

    def add_manual_peak(self, peak: int) -> bool:
        """
        Check if the manual peak is valid and if so add it to the peaks.
        """
        if not (
            peak not in self.peaks
            and peak not in self.manual_peaks
            and peak >= 0
            and peak < len(self.time)
        ):
            return False
        self.manual_peaks.append(peak)
        self.peaks = self.automatic_peaks + self.manual_peaks
        return True