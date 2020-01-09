import cv2
import scenedetect
from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.stats_manager import StatsManager

def get_scene_startFrames(filepath):
    # Create a video_manager point to video file testvideo.mp4. Note that multiple
    # videos can be appended by simply specifying more file paths in the list
    # passed to the VideoManager constructor. Note that appending multiple videos
    # requires that they all have the same frame size, and optionally, framerate.
    video_manager = VideoManager([filepath])
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)
    # Add ContentDetector algorithm (constructor takes detector options like threshold).
    scene_manager.add_detector(ContentDetector())
    base_timecode = video_manager.get_base_timecode()

    try:
        # Set downscale factor to improve processing speed.
        video_manager.set_downscale_factor()

        # Start video_manager.
        video_manager.start()

        # Perform scene detection on video_manager.
        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtain list of detected scenes.
        scene_list = scene_manager.get_scene_list(base_timecode)

        scene_startFrames = []
        for i, scene in enumerate(scene_list):
            scene_startFrames.append(scene[0].get_frames())

    finally:
        video_manager.release()

    return scene_startFrames

def crop_video(filepath, output_path='output.avi', out_size=None):
    scene_startFrame = get_scene_startFrames(filepath)

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(filepath)

    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    if int(major_ver)  < 3 :
        fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
    else :
        fps = cap.get(cv2.CAP_PROP_FPS)

    # Check if camera opened successfully
    if (cap.isOpened()== False): 
      print("Error opening video stream or file")

    ret, frame = cap.read()

    if out_size is None:
        out_size = (min(frame.shape[0],frame.shape[1]), min(frame.shape[0],frame.shape[1]))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, out_size)
    i = 0
    # Read until video is completed
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret is False:
            break
        if i in scene_startFrame:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            x_cen = 0
            y_cen = 0
            for (y,x,h,w) in faces:
                x_cen += x + w/2;
                y_cen += y + h/2;

            n_faces = len(faces)
            if n_faces > 0:
                x_cen /= n_faces
                y_cen /= n_faces
            else:
                x_cen = frame.shape[0]/2
                y_cen = frame.shape[1]/2
        
            x_min = max(0,x_cen - out_size[0]/2)
            x_max = min(x_cen + out_size[0]/2, frame.shape[0])
        
            if x_min == 0 and x_max - x_min < out_size[0]:
                x_max = min(out_size[0], frame.shape[0])
            elif x_max == frame.shape[0] and x_max - x_min < out_size[0]:
                x_min = max(0, frame.shape[0] - out_size[0])

            y_min = max(0,y_cen - out_size[1]/2)
            y_max = min(y_cen + out_size[1]/2, frame.shape[1])

            if y_min == 0 and y_max - y_min < out_size[1]:
                y_max = min(out_size[1], frame.shape[1])
            elif y_max == frame.shape[1] and y_max - y_min < out_size[1]:
                y_min = max(0, frame.shape[1] - out_size[1])
            
        frame = frame[int(x_min):int(x_max), int(y_min):int(y_max), :]
            
        out.write(frame)
        i += 1
     
    # When everything done, release the video capture object
    cap.release()
    out.release() 
    # Closes all the frames
    cv2.destroyAllWindows()