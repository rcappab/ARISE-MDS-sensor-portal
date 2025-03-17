import React, { useRef, useState } from "react";
import "../styles/drawstyles.css";
import useMousePosition from "./useMousePosition.tsx";

interface rectDrawProps {
	obsData: object[] | [];
	editMode: boolean;
	editIndex: number;
	onFinishEditing: (newBoxes: object[]) => void;
	hoverIndex: number;
}

const RectDraw = ({
	obsData = [],
	editMode = true,
	editIndex = -1,
	onFinishEditing = (newBoxes) => {},
	hoverIndex = -1,
}: rectDrawProps) => {
	const svgRef = useRef<SVGSVGElement>(null);
	const { xCord, yCord } = useMousePosition({ svgRef });
	const [mousedown, setMouseDown] = useState(false);
	const [last_mousex, set_last_mousex] = useState(0);
	const [last_mousey, set_last_mousey] = useState(0);
	const [mousex, set_mousex] = useState(0);
	const [mousey, set_mousey] = useState(0);

	// editable rect

	const [rectx, setrectx] = useState(0);
	const [recty, setrecty] = useState(0);
	const [rectwidth, setrectwidth] = useState(0);
	const [rectheight, setrectheight] = useState(0);

	const mouseDown = () => {
		set_last_mousex(xCord);
		set_last_mousey(yCord);
		setMouseDown(true);
	};

	const mouseUp = () => {
		setMouseDown(false);

		//edit bounding box array, pass new array back to parent
		const bbox = {
			x1: rectx / svgRef.current?.clientWidth,
			y1: recty / svgRef.current?.clientHeight,
			x2: (rectx + rectwidth) / svgRef.current?.clientWidth,
			y2: (recty + rectheight) / svgRef.current?.clientHeight,
		};
		console.log(bbox);
		// update the bounding box array at the edit index, pass the array back to parent
		// These states should be handled by the parent component

		obsData[editIndex]["bounding_box"] = bbox;
		onFinishEditing(obsData);
	};

	const rectFromBBox = (
		obs: object,
		index: number,
		highlight: boolean = false
	) => {
		if (
			(highlight && index !== hoverIndex) ||
			(!highlight && index === hoverIndex)
		) {
			return null;
		}
		if (!("x1" in obs["bounding_box"]) || obs["data_files"].length === 0) {
			return null;
		}

		const _rectX1 = obs["bounding_box"].x1 * svgRef.current?.clientWidth;
		const _rectY1 = obs["bounding_box"].y1 * svgRef.current?.clientHeight;
		const _rectX2 = obs["bounding_box"].x2 * svgRef.current?.clientWidth;
		const _rectY2 = obs["bounding_box"].y2 * svgRef.current?.clientHeight;

		const _rectWidth = _rectX2 - _rectX1;
		const _rectHeight = _rectY2 - _rectY1;

		console.log(obs);

		let classes = "";
		//check if human, uncertain, highlighted, apply classes

		if (obs["source"] !== "human") {
			classes += " ai-observation";
		}

		if (obs["validation_requested"]) {
			classes += " uncertain";
		}

		return (
			<>
				{highlight && index === hoverIndex ? (
					<>
						<text
							x={_rectX1}
							y={_rectY1}
							dy={-5}
							className={"label highlight"}
						>
							{obs["species_name"]}
						</text>
						<rect
							key={index}
							className={"rectangle highlight"}
							x={_rectX1}
							y={_rectY1}
							height={_rectHeight}
							width={_rectWidth}
						/>
					</>
				) : null}
				<text
					x={_rectX1}
					y={_rectY1}
					dy={-5}
					className={"label" + classes}
				>
					{obs["species_name"]}
				</text>
				<rect
					key={index}
					className={"rectangle" + classes}
					x={_rectX1}
					y={_rectY1}
					height={_rectHeight}
					width={_rectWidth}
				/>
			</>
		);
	};

	const mouseMove = () => {
		set_mousex(xCord);
		set_mousey(yCord);
	};

	const addRectangle = () => {
		if (mousedown) {
			const width = Math.abs(mousex - last_mousex);
			const height = Math.abs(mousey - last_mousey);

			const rx = mousex < last_mousex ? mousex : last_mousex;
			const ry = mousey < last_mousey ? mousey : last_mousey;
			rectx !== rx && setrectx(rx);
			recty !== ry && setrecty(ry);
			rectheight !== height && setrectheight(height);
			rectwidth !== width && setrectwidth(width);

			return (
				<rect
					className={"rectangle edit"}
					x={rx}
					y={ry}
					height={height}
					width={width}
				/>
			);
		}
	};

	const getBoxes = (highlight = false) => {
		if (editMode) {
			return addRectangle()
				? addRectangle()
				: null;
				  // <rect
				  // 	className={"rectangle"}
				  // 	x={rectx}
				  // 	y={recty}
				  // 	height={rectheight}
				  // 	width={rectwidth}
				  // />
		} else {
			return obsData.map((obsBbox, index) => {
				return rectFromBBox(obsBbox, index, highlight);
			});
		}
	};

	if (editMode) {
		return (
			<svg
				className={"rectdraw enabled"}
				ref={svgRef}
				onMouseDown={mouseDown}
				onMouseUp={mouseUp}
				onMouseMove={mouseMove}
				viewBox={`0 0 ${svgRef.current?.clientWidth} ${svgRef.current?.clientHeight}`}
			>
				{getBoxes()}
			</svg>
		);
	} else {
		return (
			<svg
				className={"rectdraw"}
				ref={svgRef}
				viewBox={`0 0 ${svgRef.current?.clientWidth} ${svgRef.current?.clientHeight}`}
			>
				<g>{getBoxes()}</g>
				<g>{getBoxes(true)}</g>
			</svg>
		);
	}
};

export default RectDraw;
