from dataclasses import dataclass


@dataclass
class VerifyModel:
    """Verification of the trained autoencoder."""

    COLORED_MODE = "COLORED"
    BLACK_MODE = "BLACK"
    KNOWN_UNKNOWN_MODE = "KNOWN_UNKNOWN"

    verify_model: bool = False
    """Verify. Runs the verification of the trained model with the options below."""

    verify_validation_set_leaks: bool = False
    """Check for validation set leaks. Verify if any of the training samples also occur in the validation
    set. Precautionary purposes. Available only for *.h5* train files."""

    show_history_plot: bool = True
    """Show history plot. Show training history plot."""

    plot_pca: bool = True
    """Plot latent space. Plot the encoder output, reduced to 3D using TruncatedSVD."""

    plot_reconstructions: bool = True
    """Plot reconstructions. Verify if the trained model is able to reconstruct the data. Main task for
    autoencoder architecture."""

    calc_recon_errors: bool = True
    """Calculate reconstruction errors. Calculates and prints total reconstruction error between
    modalities based on MSE."""

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
