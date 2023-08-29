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


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Best-README-Template</h3>

  <p align="center">
    An awesome README template to jumpstart your projects!
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template">View Demo</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Report Bug</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Request Feature</a>
  </p>
</div>



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
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
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

[![Product Name Screen Shot][product-screenshot]](https://example.com)

We are a team of four people based in Toronto, Canada.  We are developing tools to assist in the segmentation and virtual unwrapping of the Herculaneum scrolls.  Our contribution to the “Segmentation Tooling 2” competition consists of python code with the following features:

* Integration into a fork of the VolumeAnnotate project (maintained by Moshe Levy [here](https://github.com/MosheLevy20/VolumeAnnotate))
* Option to upload a pre-generated vector field for each slice to facilitate papyrus line following
* As part of the normal line-building workflow for each slice, VA now uses intelligent line finding.  This follows the vector contours of the line of the papyrus between two points.  This is in contrast to the manual generation of several straight-line segments that approximate the natural curvature of the underlying papyrus.  
* The feature reduces the number of clicks manual segmenters need to make to generate virtual fragments. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Built With


* [![Python][https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue]][https://www.python.org/]

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Prerequisites

Requirements can be installed with the following from 
  ```sh
  pip install -r requirement.txt
  ```
<!-- GETTING STARTED -->
## Getting Started

1. Create a folder of tif image slices to analyze per the normal behavior of VolumeAnnotate.  Note that in order to use the intelligent line following tool, vector field files need to be generated for each slice in the folder
2. To generate vector fields, run generate_vector_fields.py, passing the image source folder and vector field file output folder as keywords to generate the required vector field files.  
  ```sh
  python C:\path\to\input\slice\images, C:\path\to\output\vector\files
  ```
  
Note: Generating vector fields is CPU intensive.  The current implementation requires significant time to generate for each slice.  As of 2023/08/27, we have benchmarked this code as taking around 4 hours per slice with the following hardware: AMD Ryzen 7 2700x (3.7MHz, x64), 32GB RAM running Windows 10 Pro.  This time cost is impractical for the average user running off the shelf hardware, and we are aware of the limits this imposes on testing our submission.  A sample vector field generated from “06666.tif” on scroll 1 is available for download [here](https://drive.google.com/file/d/1TDmEMFlHvqm5BdxLqVw9CXD7--D-rWRH/view?usp=drive_link): (file size 2.9GB).  See the Features in Development section for more information on how we are making vector field generation run faster.  

3. From the VA-Stream folder, run VolumeAnnotate.py.  Note that some dependencies may need to be added depending on what site packages are available.  We have used the “pip install” command for installing libraries during testing.
  ```sh
  python VolumeAnnotate.py
  ```
4. From the App Startup widget, use the “Browse” button to select the folder containing the slice images described in Step 2, and then click the “Launch” button.
5. The Frame Number (shown in the text box under the “Go To Number:” label) determines which slice is being shown for annotation.  To use intelligent line following, you must connect the slice to the generated vector file.  To do this, click the “Load Slice Vector Field” button (located at bottom right), and navigate to the vector field file associated with the current slice, and click “Open”.  This will load the vector field file into VA-Stream.
6. To trace lines on the slice, zoom and pan to an area of interest using the existing VA controls.  When you are ready to trace a line, enable the radio button labeled “Outline Fragment”.  Then, left click on the image at a point on the scroll where you want to start your line.  A red dot will appear on the image.  Then, click on the part of the line you would like to join to the previous point.  VA-Stream will work to join the two points in a way that follows the “flow” of papyrus layers. 

Note: Joining points in VA-Stream is CPU intensive.  The current implementation is not instantaneous.  The other features of VA-Stream will not respond while the line joining process is in progress.  As of 2023/08/27, joining any two points on the slice takes around 10-20s.  See the Features in Development section for more information on how we are making automated line following faster. 

7. To continue the line, add more points.  VA-Stream features that involve moving points have not been tested for interaction with the line finding tool, and may cause crashes.  Use other features of VA-Stream as normal.

Note: The intelligent line finding functionality has known stability issues which may cause VA-Stream to terminate at unpredictable times.  We are working to improve the stability of this feature.  Please submit issues you encounter via the “Issues” tab on the GitHub page link above, being sure to include any information about the scroll number, slice index, and (x, y) points you deem to be associated with the instability.



### Installation

The stability of the code as of 2023/08/29 is reflective of the early stages of development and the deadlines associated with the Vesuvius Challenge.  Therefore, some special conditions apply to the user.  Our goal is to make the behavior of this tool more robust over time.  As of the submission deadline, usage instructions are as follows:

Download a local copy of the current version of VA-Stream at [https://github.com/teeohem96/VA-Stream](https://github.com/teeohem96/VA-Stream)
  ```sh
  git clone https://github.com/teeohem96/VA-Stream.git
  cd VolumeAnnotate
  ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

The following are some examples of flowlines traced using the features of this tool:

1. description, pics
2. description, pics
3. description, pics
 


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

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
