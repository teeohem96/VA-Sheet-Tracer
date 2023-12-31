from main_app.eventHandlersBase import EventHandlerBase
from .EdgeFinder import findEdges
from main_app.helpers import *
from main_app.vector_tools import *

import numpy as np
import sys
import os

##sys.path.append("C:\\Users\\Trevor\\Documents\\scroll_shell_scripts\\cv2_UI\\")
##import im2vec
##import test_dsearchn_python

class EventHandler(EventHandlerBase):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
    
    def on_mouse_mode(self, id):
        print(f"mouse mode: {id}")
        if id == 0:
            self.app.mouseMode = "Pan"
        elif id == 1:
            self.app.mouseMode = "Outline Fragment"
        elif id == 2:
            self.app.mouseMode = "Move Points"
        elif id == 3:
            self.app.mouseMode = "Delete Points"
        elif id == 4:
            self.app.mouseMode = "Insert Points"
        elif id == 5:
            self.app.mouseMode = "Label Ink"
        elif id == 6:
            self.app.mouseMode = "Mark Origin"
        else:
            print("Warning: invalid mouse mode")

    def on_unwrap_style(self, id):
        if id == 0:
            self.app.unwrapStyle = "Annotate"
        elif id == 1:
            self.app.unwrapStyle = "Project"
        else:
            print("Warning: invalid unwrap style")

    def on_annotation_color_change(self, id):
        self.app.annotationColorIdx = id
        self.app._update_image()

    def on_copy(self, event):
        # copy previous frame annotations
        self.app.image.annotations[self.app._frame_index] = copy.deepcopy(
            self.app.image.annotations[self.app._frame_index - 1]
        )
        self.app.image.interpolated[self.app._frame_index] = interpolatePoints(
            self.app.image.annotations[self.app._frame_index], self.app.image.imshape
        )
        self.app._update_image()
        autoSave(self.app)
    

    def on_load(self, event):
        # load annotations from file using pickle, pop up window to ask for file name
        filename = QFileDialog.getOpenFileName(
            self.app, "Open File", os.getcwd(), "Pickle Files (*.pkl)"
        )
        if filename[0] != "":
            with open(filename[0], "rb") as f:
                self.app.image.annotations = pickle.load(f)
                self.app.image.interpolated = pickle.load(f)
                self.app.image.imshape = pickle.load(f)

    def on_gen_vec(self, event):        
        filename = QFileDialog.getSaveFileName(
            self.app, "Save File", os.getcwd(), "Numpy Files (*.npy)"
        )
        stride, done = QInputDialog.getInt(
           self.app, 'Input Dialog', 'Enter stride (odd number):') 

        if self.app.image.origin[self.app._frame_index] is not None:
            origin = self.app.image.origin[self.app._frame_index]
        else:
            origin = (3600,3600)

        img = cv2.imread(self.app.tiffs[self.app._frame_index], cv2.IMREAD_UNCHANGED)

        # precompile njit function get_vector_field with dummy data
        # (need this or speed boost is lost for first vectorfield generation event)
        print("precompiling njit function...")
        _ = get_vector_field(img, img, 0, 0, 1, 1, np.zeros(img.shape), 1)
        print("done.")

        u, v, ub, vb, _, _ = create_vec_field(img, stride = stride, win = 100, tex_thresh = 40000, pap_thresh = 30000, origin =  origin, sub_angles = 6, alpha_v = 7e-5, sigma_v = 2.0, alpha_p = 5.0, beta_p = 2.0, gamma_p = 0.3, delta_p = 1.4, sigma = 3.0)

        print(filename[0])
        if filename[0] != "":
            stack = np.stack([u, v, ub, vb])
            stack = np.float16(stack)
            with open(filename[0], "wb") as f:
                # cast from 32bit to 16bit precision on output
                np.save(f, stack)

    def on_load_vec(self, event):
        filename = QFileDialog.getOpenFileName(
            self.app, "Open File", os.getcwd(), "Numpy Files (*.npy)"
        )
        if filename[0] != "":
            with open(filename[0], "rb") as f:
                self.app.vector_field = np.load(f)
                print('loaded vector field of shape: ')
                print(self.app.vector_field.shape)

    def on_find_origin(self, event):
        stride, done = QInputDialog.getInt(
           self.app, 'Input Dialog', 'Enter stride (odd number):') 
        img = self.app.image.img_loader.zarr_array[self.app._frame_index, :, :]
        img = np.array(img)
        origin = find_origin(img, stride)
        self.app.image.origin[self.app._frame_index] = origin
        # origin_pt = Point(origin[0]/self.app.image.imshape[0], origin[1]/self.app.image.imshape[1])
        print('Origin estimated at:')
        print(origin)
        self.app.image.origin_annotations[self.app._frame_index] = Point(origin[0]/self.app.image.imshape[1], origin[1]/self.app.image.imshape[0])
        self.app._update_image()

    def on_extrap(self, event):
        if self.app._frame_index != 0:
            if self.app.image.annotations[self.app._frame_index-1]:
                fixed = self.app.image.img_loader.zarr_array[self.app._frame_index, :, :]
                fixed = np.array(fixed)
                moving = self.app.image.img_loader.zarr_array[self.app._frame_index-1, :, :]
                moving = np.array(moving)
                demons_tx = get_demons_registration_tx(fixed, moving)
                self.app.image.annotations[self.app._frame_index] = apply_tx_to_annotations(
                    demons_tx, 
                    self.app.image.annotations[self.app._frame_index-1],
                    self.app.image.imshape
                    )

                #transform ann_list
                #self.app.image.annotations[self.app._frame_index] = self.app.image.annotations[self.app._frame_index-1]
                self.app.image.annotation_buffer[self.app._frame_index] = interp_annotation_list(
                    self.app.image.annotations[self.app._frame_index],
                    self.app.image.imshape,
                    self.app.vector_field,
                    self.app.mesh,
                    self.app.image.origin[self.app._frame_index],
                    )  

                # print(self.app.image.annotation_buffer[self.app._frame_index]) 
                self.app.image.interpolated[self.app._frame_index] = concat_annotation_buffer(self.app.image.annotation_buffer[self.app._frame_index])
                self.app._update_image()
            else:
                print("No segmentations found on previous slice!")
        else:
            print("No previous slice found!")


    def on_save(self, event):
        # save annotations to file using pickle, pop up window to ask for file name
        filename = QFileDialog.getSaveFileName(
            self.app, "Save File", os.getcwd(), "Pickle Files (*.pkl)"
        )
        if filename[0] != "":
            autoSave(self.app, filename[0])
    

    def on_save_2D(self, event):
        image2D = self.app.image.get2DImage(self.app)
        filename = QFileDialog.getSaveFileName(
            self.app, "Save File", os.getcwd(), "PNG Files (*.png)"
        )
        if filename[0] != "":
            # use cv2 to save image
            cv2.imwrite(filename[0], image2D)
    def on_export_obj(self, event):
        fname = QFileDialog.getSaveFileName(
            self.app, "Save File", os.getcwd(), "Obj Files (*.obj)"
        )
        
        exportToObj(self.app, fname[0])
    
    def on_export_to_volpkg(self, event):
        if self.app.fromVolpkg:
            fname = self.app.volpkgFolder
            Volpkg(self.app, fname)
        else:
            fname = QFileDialog.getSaveFileName(
                self.app, "Save File", os.getcwd(), "Volpkg Files (*.volpkg)"
            )
            if fname[0] != "":
                Volpkg(self.app, fname[0])

    def on_show_3D(self, event):
        nodes, full_data, offset = getPointsAndVoxels(self.app)
        
        #plot3Dmesh(np.array(nodes), full_data, offset=offset)


    def on_ink(self, event):
        self.app.update_ink()

    def on_ink_all(self, event):
        # loop through all frames and run ink detection
        for i in range(self.app._frame_count):
            self.app.update_ink(i)
        autoSave(self.app)

    def on_slider_change(self, event):
        self.app.inkThreshold = self.app.slider.value()
        self.app.update_ink()
        self.app._update_image()

    def on_show_annotations(self, event):
        self.app.show_annotations = not self.app.show_annotations
        # change the text of the button to reflect the current state
        if self.app.show_annotations:
            self.app.button_show_annotations.setText("Hide Annotations")
        else:
            self.app.button_show_annotations.setText("Show Annotations")
        self.app._update_image()

    def on_slider_ink_radius_change(self, event):
        self.app.inkRadius = self.app.slider_ink_radius.value()
        self.app.update_ink()

    def on_slider_annotation_radius_change(self, event):
        self.app.image.annotationRadius = self.app.slider_annotation_radius.value()
        self.app._update_image()


    def on_edge(self, event):
        # get the list of image names
        # imageNames = self.app._frame_list[
        #     self.app._frame_index : min(
        #         self.app._frame_index + self.app.edgeDepth, self.app._frame_count
        #     )
        # ]
        currentEdge = self.app.image.annotations[self.app._frame_index]
        if len(currentEdge) == 0:
            return
        imageIndices = list(range(
            self.app._frame_index, min(
            self.app._frame_index + self.app.edgeDepth, self.app._frame_count-1
        )))
        # use findEdges to get the list of edges
        edges = findEdges(
            currentEdge,
            imageIndices,
            self.app.loader 
        )

        # add the edges as the annotations for the next edgeDepth frames
        for i in range(1, len(edges)):
            # annotations is every n'th entry in interpolated, use slice notation
            self.app.image.annotations[self.app._frame_index + i] = edges[i]
            self.app.image.interpolated[self.app._frame_index + i] = interpolatePoints(
                edges[i], self.app.image.imshape
            )

        # run ink detection on the new annotations
        # for i in range(1, len(edges)):
        #   self.app.update_ink(self.app._frame_index + i)

        autoSave(self.app)

    def on_slider_edge_change(self, event):
        self.app.edgeDepth = self.app.slider_edge.value()
        self.app.edgeDepthTxt.setText(
            f"Num Frames = {self.app.edgeDepth}"
        )
        # self.app.label_edge.setText(f"Edge Depth: {self.app.edgeDepth}")
    def keyPressEvent(self, event):
        try:
            # Call the parent class's handle_call method
            super().keyPressEvent(event)
        except NotImplementedError:
            if event.key() == Qt.Key_C:
                # copy previous frame annotations
                self.app.image.annotations[self.app._frame_index] = copy.deepcopy(
                    self.app.image.annotations[self.app._frame_index - 1]
                )
                self.app.image.interpolated[self.app._frame_index] = interpolatePoints(
                    self.app.image.annotations[self.app._frame_index],
                    self.app.image.imshape,
                )
                #
                self.app._update_image()
                with open(self.app.sessionId, "wb") as f:
                    pickle.dump(self.app.image.annotations, f)
                    pickle.dump(self.app.image.interpolated, f)
                    pickle.dump(self.app.image.imshape, f)
            else:
                print("Key not implemented")

    def relative_point_to_pixel_point(self, relative_point):
        pixel_point = []
        print("relative_point: "+str(relative_point))

        return pixel_point
    
    def mousePressEvent(self, event):
        try:
            # Call the parent class's handle_call method
            super().mousePressEvent(event)
        except NotImplementedError:
            x, y = getRelCoords(self.app, event.globalPos())
            # check if the mouse is out of the image
            xf, yf = getImFrameCoords(self.app, event.pos())
            # xraw, yraw = getPixelCoords(self.app.image.imshape, x, y)
            if xf < 0 or yf < 0 or xf > 1 or yf > 1:
                return
            print(f"rel coords: {x}, {y}")
            print(f"frame coords: {xf}, {yf}")
            # print(f"raw coords: {xraw}, {yraw}")

            
            if self.app.mouseMode == "Outline Fragment":

                if self.app.vector_field is not None and self.app.image.origin[self.app._frame_index] is not None:
                    self.app.image.annotations[self.app._frame_index].append(Point(x, y))
                    if len(self.app.image.annotations[self.app._frame_index]) > 1:

                        # print(self.app.mesh.shape)
                        rawline = vector_trace(self.app.image.annotations[self.app._frame_index][-2:],
                            self.app.image.imshape,
                            self.app.vector_field,
                            self.app.mesh,
                            self.app.image.origin[self.app._frame_index],
                            )   

                        self.app.image.annotation_buffer[self.app._frame_index].append(rawline)
                        self.app.image.interpolated[self.app._frame_index].extend(rawline)
                    self.app._update_image()
                else: 
                    print("Missing vector field or origin!")

            elif self.app.mouseMode == "Label Ink":
                if len(self.app.image.interpolated[self.app._frame_index]) == 0:
                    return
                # find closest point
                closest = self.app.image.interpolated[self.app._frame_index][0]
                closestIndex = 0
                for p in self.app.image.interpolated[self.app._frame_index]:
                    if np.linalg.norm(
                        np.array([p.x, p.y]) - np.array([x, y])
                    ) < np.linalg.norm(np.array([closest.x, closest.y]) - np.array([x, y])):
                        closest = p
                        closestIndex = self.app.image.interpolated[
                            self.app._frame_index
                        ].index(p)
                # label ink
                closestDist = np.linalg.norm(
                    np.array([closest.x, closest.y]) - np.array([x, y])
                )

                if closestDist < 0.01:
                    self.app.image.interpolated[self.app._frame_index][
                        closestIndex
                    ].updateColor(self.app.annotationColorIdx)

            elif self.app.mouseMode == "Move Points":
                if len(self.app.image.annotations[self.app._frame_index]) == 0:
                    return
                # find closest point in annotations and start dragging
                closest = self.app.image.annotations[self.app._frame_index][0]
                closestIndex = 0
                for p in self.app.image.annotations[self.app._frame_index]:
                    if np.linalg.norm(
                        np.array([p.x, p.y]) - np.array([x, y])
                    ) < np.linalg.norm(np.array([closest.x, closest.y]) - np.array([x, y])):
                        closest = p
                        closestIndex = self.app.image.annotations[
                            self.app._frame_index
                        ].index(p)
                closestDist = np.linalg.norm(
                    np.array([closest.x, closest.y]) - np.array([x, y])
                )

                if closestDist < 0.01:
                    self.app.dragging = True
                    self.app.draggingIndex = closestIndex
                    self.app.draggingFrame = self.app._frame_index
                    self.app.draggingOffset = np.array([x, y]) - np.array(
                        [closest.x, closest.y]
                    )
                    print(f"dragging offset: {self.app.draggingOffset}")
                self.app._update_image()



            elif self.app.mouseMode == "Delete Points":
                if len(self.app.image.annotations[self.app._frame_index]) == 0:
                    return
                # find closest point in annotations and start dragging
                closest = self.app.image.annotations[self.app._frame_index][0]
                closestIndex = 0
                for p in self.app.image.annotations[self.app._frame_index]:
                    if np.linalg.norm(
                        np.array([p.x, p.y]) - np.array([x, y])
                    ) < np.linalg.norm(np.array([closest.x, closest.y]) - np.array([x, y])):
                        closest = p
                        closestIndex = self.app.image.annotations[
                            self.app._frame_index
                        ].index(p)
                closestDist = np.linalg.norm(
                    np.array([closest.x, closest.y]) - np.array([x, y])
                )

                if closestDist < 0.01:
                    
                    self.app.image.annotations[self.app._frame_index].pop(closestIndex)

                    if (closestIndex == 0) and (len(self.app.image.annotations[self.app._frame_index]) > 0): #first point deleted
                       self.app.image.annotation_buffer[self.app._frame_index].pop(closestIndex)

                    elif closestIndex != len(self.app.image.annotations[self.app._frame_index]): #middle point deleted
                        
                        self.app.image.annotation_buffer[self.app._frame_index].pop(closestIndex)
                        self.app.image.annotation_buffer[self.app._frame_index].pop(closestIndex-1)

                        newseg = vector_trace(self.app.image.annotations[self.app._frame_index][closestIndex-1:closestIndex+1],
                            self.app.image.imshape,
                            self.app.vector_field,
                            self.app.mesh,
                            self.app.image.origin[self.app._frame_index],
                            )

                        self.app.image.annotation_buffer[self.app._frame_index].insert(closestIndex-1, newseg)

                    elif (len(self.app.image.annotation_buffer[self.app._frame_index]) > 0): #last point deleted
                        self.app.image.annotation_buffer[self.app._frame_index].pop(closestIndex-1)
                    
                    self.app.image.interpolated[self.app._frame_index] = concat_annotation_buffer(self.app.image.annotation_buffer[self.app._frame_index])

                self.app._update_image()

            elif self.app.mouseMode == "Mark Origin":
                # print(self.app.image.imshape)
                self.app.image.origin[self.app._frame_index] = (int(round(x*self.app.image.imshape[1])), int(round(y*self.app.image.imshape[0])))
                print('New origin set: ')
                print(self.app.image.origin[self.app._frame_index])
                self.app.image.origin_annotations[self.app._frame_index] = Point(x, y)
                #pixel_point = self.relative_point_to_pixel_point(point)
                self.app._update_image()
            else:
                print(f"Warning: mouse mode not recognized: {self.app.mouseMode}")
        
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.app.dragging = False
    
    def mouseMoveEvent(self, event):
        try:
            super().mouseMoveEvent(event)
        except NotImplementedError:
            x, y = getRelCoords(self.app, event.globalPos())
            #print(f"dragging mouse{x,y}")
            if self.app.mouseMode == "Move Points":
                if self.app.dragging:

                    self.app.image.annotations[self.app.draggingFrame][
                        self.app.draggingIndex
                    ].x = (x - self.app.draggingOffset[0])

                    self.app.image.annotations[self.app.draggingFrame][
                        self.app.draggingIndex
                    ].y = (y - self.app.draggingOffset[1])

                    self.app.image.interpolated[self.app.draggingFrame] = interpolatePoints(
                        self.app.image.annotations[self.app.draggingFrame],
                        self.app.image.imshape,
                    )
                self.app._update_image()

            elif self.app.mouseMode == "Label Ink":
                if len(self.app.image.interpolated[self.app._frame_index]) == 0:
                    return
                if self.app.clickState == 1:
                    # find closest point
                    closest = self.app.image.interpolated[self.app._frame_index][0]
                    closestIndex = 0
                    for p in self.app.image.interpolated[self.app._frame_index]:
                        if np.linalg.norm(
                            np.array([p.x, p.y]) - np.array([x, y])
                        ) < np.linalg.norm(
                            np.array([closest.x, closest.y]) - np.array([x, y])
                        ):
                            closest = p
                            closestIndex = self.app.image.interpolated[
                                self.app._frame_index
                            ].index(p)
                    # label ink
                    closestDist = np.linalg.norm(
                        np.array([closest.x, closest.y]) - np.array([x, y])
                    )
                    # print(closestDist, "closest dist")
                    if closestDist < 0.01:
                        self.app.image.interpolated[self.app._frame_index][
                            closestIndex
                        ].updateColor(self.app.annotationColorIdx)
                    self.app._update_image()

            
            else:
                print(f"Warning: mouse mode not recognized {self.app.mouseMode}")


            
