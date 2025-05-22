import { RefObject, useEffect, useState } from "react";

interface IUseMousePosition {
	svgRef: RefObject<SVGSVGElement>;
}

export const useMousePosition = ({ svgRef }: IUseMousePosition) => {
	const [position, setPosition] = useState({ xCord: 0, yCord: 0 });

	useEffect(() => {
		function setFromEvent(e: { layerX: any; layerY: any }): void {
			return setPosition({ xCord: e.layerX, yCord: e.layerY });
		}
		if (svgRef.current) {
			svgRef.current.addEventListener("mousemove", setFromEvent);
		}

		return () => {
			if (svgRef.current) {
				svgRef.current.removeEventListener("mousemove", setFromEvent);
			}
		};
	});
	return position;
};

export default useMousePosition;
