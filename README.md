<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#prerequisites">Prerequisites</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

We are a Canadian team of four people, and we are developing tools to assist in the segmentation and virtual unwrapping of the Herculaneum scrolls.  Our contribution to the “Segmentation Tooling 2” competition consists of python code with the following features:

* Integration into a fork of the VolumeAnnotate project (maintained by Moshe Levy [here](https://github.com/MosheLevy20/VolumeAnnotate))
* Option to upload a pre-generated vector field for each slice to facilitate papyrus line following
* As part of the normal line-building workflow for each slice, VA now uses intelligent line finding.  This follows the vector contours of the line of the papyrus between two points.  This is in contrast to the manual generation of several straight-line segments that approximate the natural curvature of the underlying papyrus.  
* The feature reduces the number of clicks manual segmenters need to make to generate virtual fragments. 

The following are some examples of flowlines traced using the features of this tool:

1. Long Distance Seeds.  This is useful in situations where the flow of the line is visually well defined, and can be called easily by the segmenter
![][line_image_wide_1] ![][line_image_wide_1]

2. Moving in Traffic.  The Algorith handles crowded segments well, and allows for segmentation of crowded areas that are visually readable by a segmenter
![][line_image_wide_1] ![][line_image_crowded_1]

3. Parsing Mush.  Mushy sections can be hard to parse visually, but if the operator is confident in their judgement about where a segment starts and ends, the algorithm does a decent job of joining the two points.  
![][line_image_mush_1] ![][line_image_mush_1] 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python-shield]][Python-url]
<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

### Installation

Download a local copy of the current version of VA-Stream at [https://github.com/teeohem96/VA-Stream](https://github.com/teeohem96/VA-Stream)
  ```sh
  git clone https://github.com/teeohem96/VA-Stream.git
  cd VolumeAnnotate
  ```

### Prerequisites

Requirements can be installed with the following command: 
  ```sh
  pip install -r requirement.txt
  ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>  

<!-- USAGE EXAMPLES -->
## Usage

1. Before running the program, create a folder containing the .tif image slices you want to analyze.  These files must follow the same rules as VolumeAnnotate.  Images must be single-channel greyscale, and the filenames must be entirely numerical ("0001.tif" and "1.tif" are acceptable, "1_edit.tif" and "test.tif" are not).
2. From the VA-Stream folder, run VolumeAnnotate.py.  
  ```sh
  python VolumeAnnotate.py
  ```
3. From the App Startup widget, use the “Browse” button to select the folder containing the slice images described in Step 2, and then click the “Launch” button.
4. In order to use the intelligent line following tool, a vector field file must exist for the current slice.  Vector field files can either be loaded from an existing .npy file, or generated on the fly from the current slice.  To generate a vector field file from the current slice, click the "Generate Slice Vector Field" button.  Enter a number in the popup dialog box.  We have tested values between 3 and 151.  For preliminary work, a value of 51 is probably acceptable for most users.  
* This number represents the downsampling factor for the image.  
* The number should be odd for best performance.
* A lower number will give better line tracing at the cost of longer generation time
* A higher number will generate more quickly at the cost of tracing precision.  

Note: Generating vector field files is CPU intensive.  The current implementation requires significant time to generate for each slice.  As of 2023/08/27, we have benchmarked this code at subsampling 3 (maximum resolution) as taking around 4 hours per slice with the following hardware: 
* AMD Ryzen 7 2700x (3.7MHz, x64), 
* 32GB RAM 
* Windows 10 Pro.  
This time cost is impractical for the average user running off the shelf hardware, and we are aware of the limits this imposes on testing our submission.  We have uploaded pre-generated vector field files from Scroll 1 for slice indices [06666.tif](https://drive.google.com/file/d/1WT_rrzDXcYBfrOApCxgztPIua6jBHAcA/view?usp=drive_link), [06667.tif](https://drive.google.com/file/d/1u47Yt-a98yJ-fK3PVwOMDkF__MKRTSye/view?usp=drive_link), [06668.tif](https://drive.google.com/file/d/1nCq1sz4PbqTYPB_ob3k2V_nWN43lF9DO/view?usp=drive_link) are available for download: (file size 487MB).  See the Roadmap section for more information on how we are making vector field generation run faster.  

5. To load an existing vector field file, click the “Load Slice Vector Field” button, and navigate to the vector field file associated with the current slice.  When generated, these files will have the same name as the slice image in the numpy format (e.g. slice 01234.tif will generate vector field file 01234.npy).  Select the file and click “Open”.  This will load the vector field file into VA-Stream.
6. To trace lines on the slice, zoom and pan to an area of interest using the existing VA controls.  When you are ready to trace a line, enable the radio button labeled “Outline Fragment”.  Then, left click on the image at a point on the scroll where you want to start your line.  Aim for an existing line of papyrus.  A red dot will appear on the image.  Then, click on the part of the line you would like to join to the previous point.  VA-Stream will work to join the two points in a way that follows the “flow” of papyrus layers. 

Note: Joining points in VA-Stream is CPU intensive.  The current implementation is not instantaneous.  The other features of VA-Stream will not respond while the line joining process is in progress.  As of 2023/08/27, joining any two points on the slice takes around 10-20s.  See the Roadmap section for more information on how we are making automated line following faster. 

7. To continue the line, add more points.  VA-Stream features that involve moving points have not been tested for interaction with the line finding tool, and may cause crashes.  Use other features of VA-Stream as normal.

Note: The intelligent line finding functionality has known stability issues which may cause VA-Stream to terminate at unpredictable times.  We are working to improve the stability of this feature.  Please submit issues you encounter via the “Issues” tab on the GitHub page link above, being sure to include any information about the scroll number, slice index, and (x, y) points you deem to be associated with the instability.
 
To generate vector fields in advance and in bulk, run generate_vector_fields.py, passing the image source folder and vector field file output folder as keywords to generate the required vector field files.  
  ```sh
  python generate_vector_fields.py C:\path\to\input\slice\images, C:\path\to\output\vector\files
  ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

User Interface Features:
- [ ] Intelligent point dragging
- [ ] Intelligent point insertion
- [X] Intelligent point deletion
- [ ] Automatic Slice-Vector file matching
- [ ] Shift+Mouse-move for speculative intelligent line overlay

Backend Features:
- [ ] Hardware acceleration
- [ ] Replace matplotlib streamplot with more efficient Runge-Kutta 2 integrator
- [ ] Automated origin detection (slice spiral “center”)
- [ ] Automated point seeding 
- [ ] Automated generation of vector field data for scalable analysis
- [ ] Interlayer context detection to avoid flowline intersection
- [ ] Z-axis interpolation using optical flow + displacement mapping
- [ ] Improved contextual line following using known segments
- [ ] Live confidence metrics 

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the GPL-v3 License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

Tom Wei - tom.wei@mail.utoronto.ca
Trevor Plint - trevor.plint@mail.utoronto.ca

Project Link: [https://github.com/teeohem96/VA-Stream](https://github.com/teeohem96/VA-Stream)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* This project is built on top of code developed by [Moshe Levy](https://github.com/MosheLevy20), without whose efforts this tool would not have been possible.  
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->


[Python-shield]: https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue
[Python-url]: python.org 
[line_image_wide_1]:https://github.com/teeohem96/VA-Sheet-Tracer/blob/master/example_traces/VA_stream_line_wide1_image.png
[line_image_wide_2]:https://github.com/teeohem96/VA-Sheet-Tracer/blob/master/example_traces/VA_stream_line_wide2_image.png
[line_image_crowded_1]:https://github.com/teeohem96/VA-Sheet-Tracer/blob/master/example_traces/VA_stream_line_crowded1_image.png
[line_image_crowded_2]:https://github.com/teeohem96/VA-Sheet-Tracer/blob/master/example_traces/VA_stream_line_crowded2_image.png
[line_image_mush_1]:https://github.com/teeohem96/VA-Sheet-Tracer/blob/master/example_traces/VA_stream_line_mush1_image.png
[line_image_mush_2]:https://github.com/teeohem96/VA-Sheet-Tracer/blob/master/example_traces/VA_stream_line_mush2_image.png
