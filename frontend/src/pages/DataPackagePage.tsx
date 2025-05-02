import React from "react";
import { useContext } from "react";
import AuthContext from "../context/AuthContext";
import { deleteData, getData } from "../utils/FetchFunctions.js";
import { useQuery, keepPreviousData, useMutation } from "@tanstack/react-query";
import Loading from "../components/Loading.tsx";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";

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

	// DELETE FUNCTIONS

	const newDELETE = async function (objID) {
		let response_json = await deleteData(
			`datapackage/${objID}`,
			authTokens.access
		);
		return response_json;
	};

	const doDelete = useMutation({
		mutationFn: (objID) => newDELETE(objID),
	});

	const deleteItem = async function (objID, name) {
		let response = await doDelete.mutateAsync(objID);
		console.log(response);
		if (response["ok"]) {
			toast(`Deleted ${name}`);
			refetch();
		}
	};

	if ((isLoading || isPending || isRefetching) && !isPlaceholderData) {
		return <Loading />;
	}

	return (
		<div>
			<h3>Your data packages</h3>
			<table className="table">
				<thead className="table-dark">
					<tr>
						<th> Name </th>
						<th> Status </th>
						<th> </th>
						<th> </th>
					</tr>
				</thead>
				<tbody>
					{data.map((dataPackage) => {
						return (
							<tr key={dataPackage["name"]}>
								<td>{dataPackage["name"]}</td>
								<td>{dataPackage["status"]}</td>
								<td>
									{dataPackage["status"] === "Ready" ? (
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
								<td>
									{["Ready", "Failed"].includes(dataPackage["status"]) ? (
										<div>
											<button
												type="button"
												className="btn btn-danger"
												onClick={(e) =>
													deleteItem(dataPackage["id"], dataPackage["name"])
												}
											>
												Delete
											</button>
										</div>
									) : null}
								</td>
							</tr>
						);
					})}
				</tbody>
			</table>
		</div>
	);
};

export default DataPackagePage;
