import AudioPlayer from "react-h5-audio-player";
import "react-h5-audio-player/lib/styles.css";
import React from "react";

interface AudioProps {
	src: string;
}

const Audio = ({ src }: AudioProps) => {
	return <AudioPlayer src={src} />;
};

export default Audio;
