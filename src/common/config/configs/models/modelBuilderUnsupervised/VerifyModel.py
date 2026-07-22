from dataclasses import dataclass


@dataclass
class VerifyModel:
    COLORED_MODE = "COLORED"
    BLACK_MODE = "BLACK"
    KNOWN_UNKNOWN_MODE = "KNOWN_UNKNOWN"

    verify_model: bool = True
    verify_validation_set_leaks: bool = False
    show_history_plot: bool = True
    plot_pca: bool = True
    plot_reconstructions: bool = True
    calc_recon_errors: bool = True

    def is_verify_validation_set_leaks(self):
        return self.verify_model and self.verify_validation_set_leaks

    def is_show_history_plot(self):
        return self.verify_model and self.show_history_plot

    def is_plot_pca(self):
        return self.verify_model and self.plot_pca

    def is_plot_reconstructions(self):
        return self.verify_model and self.plot_reconstructions

    def is_calc_recon_errors(self):
        return self.verify_model and self.calc_recon_errors
