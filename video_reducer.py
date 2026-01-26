import cv2
import sys
import os


def reduce_video(input_path):

    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        print("Cannot open video")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(3))
    height = int(cap.get(4))

    output_path = input_path.replace(".mp4", "_reduced.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(
        output_path,
        fourcc,
        fps // 2,
        (width // 2, height // 2)
    )

    frame_id = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        # Skip every other frame
        if frame_id % 2 == 0:

            small = cv2.resize(
                frame,
                (width // 2, height // 2)
            )

            out.write(small)

        frame_id += 1


    cap.release()
    out.release()

    print("Saved:", output_path)


if __name__ == "__main__":

    video = sys.argv[1]

    reduce_video(video)
