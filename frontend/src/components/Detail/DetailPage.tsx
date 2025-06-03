import React, { useContext, useState } from "react";
import DetailModalContent from "./DetailModalContent.tsx";
import { useNavigate } from "react-router-dom";
import { deleteData, getData } from "../../utils/FetchFunctions";
import { useMutation, useQuery } from "@tanstack/react-query";
import AuthContext from "../../context/AuthContext";
import Loading from "../General/Loading.tsx";
import toast from "react-hot-toast";
import DetailDisplayUser from "./DetailDisplayUser.tsx";
import { useObjectType } from "../../context/ObjectTypeCheck.tsx";
import Error404page from "../../pages/Error404page.jsx";

const DetailPage = () => {
	const { authTokens, user } = useContext(AuthContext);
	const { fromID, objectType, nameKey } = useObjectType();
	if (objectType === "user") {
		return (
			<DetailDisplayUser
				id={fromID}
				authTokens={authTokens}
				user={user}
			/>
		);
	} else {
		return (
			<ObjectDetailPage
				authTokens={authTokens}
				user={user}
				fromID={fromID}
				objectType={objectType}
				nameKey={nameKey}
			/>
		);
	}
};

interface DetailProps {
	authTokens: any;
	user: any;
	fromID: string | undefined;
	objectType: string | undefined;
	nameKey: string;
}

const ObjectDetailPage = ({
	authTokens,
	user,
	fromID,
	objectType,
	nameKey,
}: DetailProps) => {
	const [editMode, setEditMode] = useState(false);
	const navigate = useNavigate();

	const getDataFunc = async () => {
		let apiURL = `${objectType}/${fromID}`;
		let response_json = await getData(apiURL, authTokens.access);
		return response_json;
	};

	const {
		isLoading,
		//isError,
		isPending,
		data,
		//error,
		//isPlaceholderData,
		refetch,
	} = useQuery({
		queryKey: ["data", user, fromID],
		queryFn: () => getDataFunc(),
		refetchOnWindowFocus: false,
	});

	const newDELETE = async function (objID) {
		let response_json = await deleteData(
			`${objectType}/${objID}`,
			authTokens.access
		);
		return response_json;
	};

	const doDelete = useMutation({
		mutationFn: (objID) => newDELETE(objID),
	});

	const deleteItem = async function (objID) {
		let response = await doDelete.mutateAsync(objID);
		if (response["ok"]) {
			toast(`Deleted ${data[nameKey]}`);
			navigate(`/${objectType}s`);
		}
	};

	if (isLoading || isPending) {
		return <Loading />;
	}

	const canEdit = data["user_is_manager"];
	const canDelete = data["user_is_owner"];

	const editButton = () => {
		if (canEdit) {
			return (
				<div className={`form-check form-switch col-auto pt-3`}>
					<label htmlFor="post-autoupdate">Edit</label>
					<input
						name="editMode"
						className="form-check-input form-control"
						id="set-editMode"
						value={editMode ? "true" : "false"}
						checked={editMode}
						type="checkbox"
						onChange={(e) => {
							setEditMode(e.target.checked);
						}}
					/>
				</div>
			);
		}
	};

	const deleteButton = () => {
		if (canDelete) {
			return (
				<div className="col-auto">
					<button
						type="button"
						className="btn btn-danger btn-lg ms-lg-2 me-lg-2"
						onClick={() => {
							deleteItem(fromID);
						}}
					>
						Delete
					</button>
				</div>
			);
		}
	};

	if (objectType === undefined) {
		return <Error404page />;
	}

	return (
		<>
			<div className="row">
				<h1 className="col-auto">{data[nameKey]}</h1>
				{editButton()}
				{deleteButton()}
			</div>
			<DetailModalContent
				objectType={objectType}
				selectedData={data}
				editMode={editMode}
				onCancel={() => {
					setEditMode(false);
				}}
				onSubmit={() => {
					refetch();
				}}
			/>
		</>
	);
};

export default DetailPage;
