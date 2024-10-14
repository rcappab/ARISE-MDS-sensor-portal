import React from "react";
import { dtFormat } from "../utils/timezoneFunctions";

interface Props {
	selectedData: object;
}

const DetailDisplay = ({ selectedData }: Props) => {
	const hideKeys = ["combo_project", "last_imageURL"];
	const timeKeys = [
		"created_on",
		"modified_on",
		"recording_dt",
		"deploymentStart",
		"deploymentEnd",
	];

	const convertDates = function (key, value) {
		if (timeKeys.includes(key)) {
			let currentTime = value;

			console.log(currentTime);
			let dateTime = new Date(currentTime);
			console.log(dateTime);
			return dtFormat.format(dateTime);
		} else {
			return value;
		}
	};

	const tableRow = function (key, value) {
		if (hideKeys.includes(key)) {
			return null;
		}

		value = convertDates(key, value);

		let value_result;

		if (key == "extra_info") {
			value_result = (
				<td className="extra-info-table p-0 border">
					<table className="table table-sm mb-0 align-middle text-center">
						<tbody>
							{Object.keys(value).map((e_iKey, i) => {
								return (
									<tr>
										<th scope="row">{e_iKey}</th>
										<td>{value[e_iKey]}</td>
									</tr>
								);
							})}
						</tbody>
					</table>
				</td>
			);
		} else {
			value_result = <td>{value === null ? value : String(value)}</td>;
		}

		return (
			<tr>
				<th scope="row">{key}</th>
				{value_result}
			</tr>
		);
	};

	return (
		<div id="detail-display">
			<table className="table detail-table">
				<tbody>
					{Object.keys(selectedData).map((key, i) => {
						return tableRow(key, selectedData[key]);
					})}
				</tbody>
			</table>
		</div>
	);
};

export default DetailDisplay;
