def set_style_sheet(self, path):
    with open(path,"r") as fh:
        self.setStyleSheet(fh.read())