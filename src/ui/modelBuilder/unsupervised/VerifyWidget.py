from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout


from src.common.config.configs.models.modelBuilderUnsupervised import VerifyModel
from src.common.config import Config
from src.common.config.configs import ModelBuilderUnsupervisedConfig

from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.dataViewer import SettingsSignals

from src.ui.modelBuilder import scaler as scaler
from src.ui.common import BannerWidget
from src.core import PathHelper

from src.ui.common import DirectorySelectorWidget
from src.ui.modelBuilder.unsupervised.HdbscanWidget import HdbscanWidget
from src.ui.modelBuilder.unsupervised.UmapWidget import UmapWidget
from src.ui.modelBuilder.unsupervised.MiniBatchKMeansWidget import MiniBatchKMeansWidget
from src.ui.modelBuilder.unsupervised.KMeansWidget import KMeansWidget


class VerifyWidget(QWidget):
    def __init__(self, singals: SettingsSignals):
        super().__init__()
        self.config: VerifyModel = Config.get(
            ModelBuilderUnsupervisedConfig
        ).verify_model
        self._value = self.config
        self._value_original = self.config

        self.verify_validation_set_leaks_widget = MeasurementWidget(
            self.config.verify_validation_set_leaks,
            label="Check for validation set leaks",
            tooltip="Verify if any of the test set samples do not occur in validation set. Precautionary purposes.",
            value_changed=singals.value_changed,
            children=[],
            layout="Vertical",
            margins=(10, 5, 0, 0),
        )

        self.show_history_plot_widget = MeasurementWidget(
            self.config.show_history_plot,
            label="Show history plot",
            tooltip="Show training history plot",
            value_changed=singals.value_changed,
            children=[],
            layout="Vertical",
            margins=(10, 5, 0, 0),
        )

        self.plot_pca_widget = MeasurementWidget(
            self.config.plot_pca,
            label="Plot latent space",
            tooltip="Plot the encoder output, reduced to 3D using TruncatedSVD",
            value_changed=singals.value_changed,
            children=[],
            layout="Vertical",
            margins=(10, 5, 0, 0),
        )

        self.plot_reconstructions_widget = MeasurementWidget(
            self.config.plot_reconstructions,
            label="Plot reconstructions",
            tooltip="Verify if trained model is able to reconstruct the data. Main task for autoencoder architecture.",
            value_changed=singals.value_changed,
            children=[],
            layout="Vertical",
            margins=(10, 5, 0, 0),
        )

        self.calc_recon_errors_widget = MeasurementWidget(
            self.config.calc_recon_errors,
            label="Calculate reconstruction errors",
            tooltip="Calculates and prints total reconstruction error between modalities based on MSE",
            value_changed=singals.value_changed,
            children=[],
            layout="Vertical",
            margins=(10, 5, 0, 0),
        )

        self.verify_model_widget = MeasurementWidget(
            self.config.verify_model,
            label="Verify",
            tooltip="",
            value_changed=singals.value_changed,
            children=[
                # self.verify_validation_set_leaks_widget,
                self.show_history_plot_widget,
                self.plot_pca_widget,
                self.plot_reconstructions_widget,
                self.calc_recon_errors_widget,
            ],
            layout="Vertical",
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.verify_model_widget)
        layoutV.addStretch()
        layoutV.setSpacing(0)

        self.setLayout(layoutV)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

    @property
    def value(self):
        if self.verify_model_widget.value == True:
            self._value.verify_model = True
            self._value.verify_validation_set_leaks = (
                self.verify_validation_set_leaks_widget.value
            )
            self._value.show_history_plot = self.show_history_plot_widget.value
            self._value.plot_pca = self.plot_pca_widget.value
            self._value.plot_reconstructions = self.plot_reconstructions_widget.value
            self._value.calc_recon_errors = self.calc_recon_errors_widget.value
        else:
            self._value = self._value_original
            self._value.verify_model = False

        return self._value

    @value.setter
    def value(self, value):
        self._value = value
