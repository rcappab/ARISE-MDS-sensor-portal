import React from "react";
import Plot from "react-plotly.js";
import { capitalizeFirstLetter } from "../../utils/generalFunctions.js";

interface Props {
	data: object;
}

const MetricPlot = ({ data }: Props) => {
	console.log(data);
	return (
		<Plot
			data={[
				{
					x: data["x_values"],
					y: data["y_values"],
					type: "scatter",
					mode: "lines+markers",
					marker: { color: "red" },
					name: "",
				},
				{
					type: "bar",
					x: data["x_values"],
					y: data["y_values"],
					marker: { color: "steelblue" },
					name: "",
				},
			]}
			layout={{
				showlegend: false,
				title: {
					text: capitalizeFirstLetter(data["name"].replace(/_/g, " ")),
				},
				xaxis: {
					title: { text: data["x_label"].replace(/_/g, " ") },
					tickformat: "%Y-%m-%d",
				},
				yaxis: {
					title: {
						text: capitalizeFirstLetter(data["y_label"].replace(/_/g, " ")),
					},
				},
			}}
			config={{ responsive: true }}
		/>
	);
};

export default MetricPlot;
