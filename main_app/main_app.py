from .mImage import mImage
from .helpers import *
from . import modes
from .loading import Loader, RemoteZarr, load_tif
import importlib
import numpy as np

# unique session id including timestamp, for autosaving progress
sessionId0 = time.strftime("%Y%m%d%H%M%S") 
sessionId = sessionId0 + "autosave.pkl"

class App(QWidget):
    def __init__(self, *args, STREAM=False, scroll="scroll1", mode="classic", downpath=None, folder=None):
        super().__init__(*args)
        self.mode = importlib.import_module(f'{modes.__name__}.{mode}')

        self.EH = self.mode.eventHandlers.EventHandler(self)

        self.sessionId = sessionId
        self.sessionId0 = sessionId0

        t0 = time.time()
        self.loaderSmall = None
        if STREAM:
            urls = {"scroll1":"http://dl.ash2txt.org/full-scrolls/Scroll1.volpkg/volumes_masked/20230205180739/"}
            #"scroll2":"http://dl.ash2txt.org/full-scrolls/Scroll2.volpkg/volumes_masked/20230210143520/",
            #}
            urlsSmall = {"scroll1":"http://dl.ash2txt.org/full-scrolls/Scroll1.volpkg/volumes_small/20230205180739/"}
            #            "scroll2":"http://dl.ash2txt.org/full-scrolls/Scroll2.volpkg/volumes_small/20230210143520/",}
            # urlsCubes = {"scroll1":"http://dl.ash2txt.org/full-scrolls/Scroll1.volpkg/volume_grids/20230205180739/",
            #            "scroll2":"http://dl.ash2txt.org/full-scrolls/Scroll2.volpkg/volume_grids/20230210143520/",}
            
            urlsCubes = {"scroll1":"http://dl.ash2txt.org/full-scrolls/Scroll1.volpkg/volume_tiles/20230205180739/"}
            #            "scroll2":"http://dl.ash2txt.org/full-scrolls/Scroll2.volpkg/volume_grids/20230210143520/",}

            username = "registeredusers"
            password = "only"
            #dialog box select scroll1 or scroll2
            scroll = QInputDialog.getItem(self, "Select Scroll", "Scroll:", list(urls.keys()), 0, False)[0]
            self.scroll = scroll

            #downpath = QFileDialog.getExistingDirectory(self, "Select Directory to Download Images", os.getcwd())
            downpath = os.path.join(os.getcwd(), "tempDown")
            downpathCubes = os.path.join(downpath, scroll+"_cubeDownloads")
            downpathSmall = os.path.join(downpath, scroll+"_smallDownloads")
            #check if downpath exists
            if not os.path.exists(downpathCubes):
                os.makedirs(downpathCubes)
            if not os.path.exists(downpathSmall):
                os.makedirs(downpathSmall)

            img_array_cubes = RemoteZarr(urlsCubes[scroll], username, password, downpathCubes, chunk_type="cuboid", max_storage_gb=20)
            img_array_small = RemoteZarr(urlsSmall[scroll], username, password, downpathSmall, chunk_type="zstack", max_storage_gb=20)
            self.loader = Loader(img_array_cubes, STREAM,chunk_type="cuboid", max_mem_gb=3)
            self.loaderSmall = Loader(img_array_small, STREAM, chunk_type="zstack", max_mem_gb=3)
        else:
            print(folder)
            if folder.endswith(".volpkg"):
                self.fromVolpkg = True
                self.volpkgFolder = folder
                # vol = os.listdir(os.join(folder,"volumes"))[0]
                #create pop up to select volume
                self.vol = QFileDialog.getExistingDirectory(self, "Select Volume", os.path.join(folder,"volumes"))
                img_array, tiffs = load_tif(self.vol)
            else:
                self.fromVolpkg = False
                img_array, tiffs = load_tif(folder)
                print(tiffs)
                self.tiffs = [folder + "/" + t for t in tiffs]
            print(f"img_array: {img_array.shape}")
            self.loader = Loader(img_array, STREAM, max_mem_gb=32)
        

        self._frame_index = 0
        if STREAM:
            self._frame_count = img_array_small.file_list.shape[0]
        else:
            self._frame_count = img_array.shape[0]
        # add text for frame number, non editable
        print("Initializing image")
        self.image = mImage(self._frame_count, self.loader, self.loaderSmall)
        pmap = self.image.getImg(0)
        print(pmap)
        self.label = ImageLabel(pmap, self)
        print(self.loader.shape, "Lshape")
        print("Finished pixmap")

        self.vector_field = None
        self.mesh = np.mgrid[0:img_array.shape[1], 0:img_array.shape[2]]
        self.mesh = np.flip(self.mesh, 0) #permute axes to return x coordinate first
        #print(self.mesh.shape)
        #print(self.mesh[0])
        #self.origin = (3758,3531)

        if self.image.img is None:
            self.image.getImg(self._frame_index)
        self.panLen = self.image.img.width() / 5

        # set grid layout, and assign widgets to app attributes
        self.mode.layout.getLayoutItems(self)
        
        self.setLayout(self.layout)

        self.dragging = False
        self.draggingIndex = -1
        self.draggingPoint = None
        self.draggingOffset = None
        self.panning = False
        self.clickState = 0
        self.STREAM = STREAM
        self.show()        

    @property 
    def pixelSize0(self):
        image_rect = self.label.rect()
        return self.image.loaded_shape[0] / image_rect.height()

    @property
    def pixelSize1(self):
        image_rect = self.label.rect()
        return self.image.loaded_shape[1] / image_rect.width()

    def _update_frame(self):
        # self.image.setImg(self._frame_index)
        self.frame_number.setText(f"Frame: {self._frame_index+1}/{self._frame_count}")
        if self.image.origin[self._frame_index] is None:
            print('origin finder called from here')
            # img = self.image.img_loader.zarr_array[self._frame_index, :, :]
            # self.image.origin[self._frame_index] = find_origin(img)
        self._update_image()

    def _update_image(self):
        # pmap = self.image.getImg(self._frame_index, self.show_annotations)
        # pmap = self.label.pixmap()
        # self.label.setPixmap(pmap)
        self.label.update()
        #pass

    def keyPressEvent(self, event):
        return self.EH.keyPressEvent(event)

    def mousePressEvent(self, event):
        return self.EH.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        return self.EH.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        return self.EH.mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        return self.EH.wheelEvent(event)
    





class StartupDialog(QDialog):
    def __init__(self, *args):
        super().__init__()
        self.app = args[0]
        #get list of all folders in modes
        modePath = os.path.dirname(modes.__file__)
        #get all folders in modes that contain __init__.py
        modeFolders = [f for f in os.listdir(modePath) if os.path.isdir(os.path.join(modePath, f)) and "__init__.py" in os.listdir(os.path.join(modePath, f))]
        self.setWindowTitle("Select data source")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(400, 200)
        
        # Set up the layout
        layout = QVBoxLayout()


        # Add a label
        layout.addWidget(QLabel("Select data source:"))

        # Add radio buttons for data source options
        self.stream_data = QRadioButton("Stream data (Semi-functional)")
        #layout.addWidget(QLabel("Stream data disabled for now"))
        self.local_data = QRadioButton("Load data")
        layout.addWidget(self.stream_data)
        layout.addWidget(self.local_data)

        # Add a button to browse for a local directory (disabled by default)
        #add text for directory selection
        layout.addWidget(QLabel("Select local directory:"))
        self.browse_button = QPushButton("Browse")
        self.browse_button.setEnabled(True)
        layout.addWidget(self.browse_button)

        # Add a line edit to display the selected local directory path
        self.directory_path = QLineEdit()
        self.directory_path.setEnabled(False)
        layout.addWidget(self.directory_path)

        #add a mode selection dropdown
        self.modeSelect = QComboBox()
        self.modeSelect.addItems(modeFolders)
        #add text for mode selection
        layout.addWidget(QLabel("Select mode:"))
        layout.addWidget(self.modeSelect)


        # Add a launch button
        launch_button = QPushButton("Launch")
        layout.addWidget(launch_button)

        # Connect signals and slots
        self.stream_data.toggled.connect(self.update_browse_button)
        self.browse_button.clicked.connect(self.browse_for_directory)
        launch_button.clicked.connect(self.launch_app)

        # Set the default selection
        self.local_data.setChecked(True)

        # Set the layout and window title
        self.setLayout(layout)
        self.setWindowTitle("App Startup")

    def update_browse_button(self, checked):
        if checked:
            self.browse_button.setEnabled(False)
            self.directory_path.setEnabled(False)
        else:
            self.browse_button.setEnabled(True)
            self.directory_path.setEnabled(True)

    def browse_for_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directory_path.setText(directory)

    def launch_app(self):
        self.accept()
        print(f"stream: {self.stream_data.isChecked()}")
        #folder = 'C:\\Users\\Tom\\Documents\\Vesuvius\\VolumeAnnotate\\VolumeAnnotate\\cropsmall'
        #win = App(STREAM=self.stream_data.isChecked(), folder=folder, mode=self.modeSelect.currentText(), downpath="downTemp") 
        win = App(STREAM=self.stream_data.isChecked(), folder=self.directory_path.text(), mode=self.modeSelect.currentText(), downpath="downTemp")
        print("App initialized")

def run():
    app = QApplication([])
    startup = StartupDialog(app)
    startup.exec()
    app.exec()
if __name__ == "__main__":
    run()
    
