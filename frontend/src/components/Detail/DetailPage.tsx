import React, { useContext, useState } from "react";
import DetailModalContent from "./DetailModalContent.tsx";
import { useParams } from "react-router-dom";
import { getData } from "../../utils/FetchFunctions";
import { useQuery } from "@tanstack/react-query";
import AuthContext from "../../context/AuthContext";
import Loading from "../Loading.tsx";
interface Props {
	objectType: string;
	nameKey: string;
}
const DetailPage = ({ objectType, nameKey }: Props) => {
	const { authTokens, user } = useContext(AuthContext);
	const { id } = useParams();
	const [editMode, setEditMode] = useState(false);

	const getDataFunc = async () => {
		let apiURL = `${objectType}/?id=${id}`;
		console.log(apiURL);
		let response_json = await getData(apiURL, authTokens.access);
		return response_json[0];
	};

	const {
		isLoading,
		isError,
		isPending,
		data,
		error,
		isPlaceholderData,
		refetch,
	} = useQuery({
		queryKey: ["data", user, id],
		queryFn: () => getDataFunc(),
	});

	if (isLoading || isPending) {
		return <Loading />;
	}

	return (
		<>
			<div className="row">
				<h1 className="col-auto">{data[nameKey]}</h1>
				<div className={`form-check form-switch col-auto`}>
					{" "}
					<label htmlFor="post-autoupdate">Auto update</label>
					<input
						name="editMode"
						className="form-check-input form-control"
						id="set-editMode"
						value={editMode ? "true" : "false"}
						type="checkbox"
						onChange={(e) => {
							setEditMode(e.target.checked);
						}}
					/>
				</div>
			</div>
			<DetailModalContent
				objectType={objectType}
				selectedData={data}
				editMode={editMode}
			/>
		</>
	);
};

export default DetailPage;
