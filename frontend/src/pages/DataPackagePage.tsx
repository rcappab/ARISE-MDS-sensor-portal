import React from "react";
import { useContext } from "react";
import AuthContext from "../context/AuthContext";
import { getData } from "../utils/FetchFunctions.js";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import Loading from "../components/Loading.tsx";
import { Link } from "react-router-dom";

const DataPackagePage = () => {
	const { authTokens, user } = useContext(AuthContext);

	const getDataFunc = async () => {
		let apiURL = `${"datapackage"}/`;
		console.log(apiURL);
		let response_json = await getData(apiURL, authTokens.access);
		return response_json;
	};

	const {
		isLoading,
		isError,
		isPending,
		data,
		error,
		isRefetching,
		isPlaceholderData,
		refetch,
	} = useQuery({
		queryKey: ["datapackage", user],
		queryFn: () => getDataFunc(),
		refetchOnWindowFocus: false,
		placeholderData: keepPreviousData,
	});

	if ((isLoading || isPending || isRefetching) && !isPlaceholderData) {
		return <Loading />;
	}

	return (
		<div>
			<table className="table">
				<tr>
					<th> Name </th>
					<th> Status </th>
					<th> </th>
				</tr>
				{data.map((dataPackage) => {
					return (
						<tr>
							<td>{dataPackage["name"]}</td>
							<td>{dataPackage["status"]}</td>
							<td>
								{dataPackage["file_url"] ? (
									<Link
										to={`/${dataPackage["file_url"]}`}
										target="_blank"
									>
										<button
											type="button"
											className="btn btn-primary"
										>
											Download
										</button>
									</Link>
								) : null}
							</td>
						</tr>
					);
				})}
			</table>
		</div>
	);
};

export default DataPackagePage;
