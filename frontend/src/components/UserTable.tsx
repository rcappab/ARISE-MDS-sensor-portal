import React from "react";

interface Props {
	tableID: string;
	userData?: [];
	button?: boolean;
	buttonOnClick?: () => void;
	buttonClass?: string;
	buttonText?: string;
}

const UserTable = ({
	tableID = "",
	userData = [],
	button = false,
	buttonOnClick = () => {},
	buttonClass = "",
	buttonText = "",
}: Props) => {
	const tableRow = (currentData, index) => {
		console.log(currentData);
		return (
			<tr key={index}>
				{Object.keys(currentData).map((key, i) => {
					return <td key={`${index}_${key}`}>{currentData[key]}</td>;
				})}
			</tr>
		);
	};

	const tableHead = (currentData) => {
		console.log(currentData);
		return (
			<tr key={0}>
				{Object.keys(currentData).map((key, i) => {
					return (
						<th
							key={`0_${key}`}
							id={`0_${key}`}
						>
							{key}
						</th>
					);
				})}
			</tr>
		);
	};

	if (userData.length === 0) {
		return;
	}

	return (
		<table>
			<thead>{tableHead(userData[0])}</thead>
			<tbody>
				{userData.map((currentData, i) => {
					return tableRow(currentData, i);
				})}
			</tbody>
		</table>
	);
};

export default UserTable;
