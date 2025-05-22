import React, { useContext } from "react";
import { useQuery } from "@tanstack/react-query";
import { getData } from "../../utils/FetchFunctions";
import AuthContext from "../../context/AuthContext";

interface Props {
	selectedDataID: number;
}

const DetailDisplayStorage = ({ selectedDataID }: Props) => {
	const { authTokens } = useContext(AuthContext);

	const getDataFunc = async () => {
		let apiURL = `datastorageinput/${selectedDataID}`;
		let response_json = await getData(apiURL, authTokens.access);
		return response_json;
	};

	const { isLoading, data } = useQuery({
		queryKey: ["datastorageinput", selectedDataID],
		queryFn: () => getDataFunc(),
	});

	if (!data || isLoading) {
		return null;
	}

	return (
		<div className="row">
			<div className="col-12 col-md-4">
				<strong>Storage name: </strong> {data.name}
			</div>
			<div className="col-12 col-md-4">
				<strong>Address: </strong>
				{data.address}
			</div>
		</div>
	);
};

export default DetailDisplayStorage;
