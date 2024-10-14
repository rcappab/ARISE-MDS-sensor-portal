import React from "react";
import { useState, useEffect, useContext, useCallback } from "react";
import { deleteData, getData } from "../../utils/FetchFunctions.js";
import AuthContext from "../../context/AuthContext.jsx";
import GalleryForm from "./GalleryForm.tsx";
import GalleryDisplay from "./GalleryDisplay.tsx";
import GalleryPageControls from "./GalleryPageControls.tsx";
import Modal from "../Modal.tsx";
import DetailModalHeader from "../Detail/DetailModalHeader.jsx";
import DetailDisplay from "../Detail/DetailDisplay.tsx";
import DeploymentDetailEdit from "../Detail/DeploymentDetailEdit.tsx";
import Loading from "../Loading.tsx";
import { useQuery, keepPreviousData, useMutation } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";

interface Props {
	objectType: string;
	nameKey: string;
}

const Gallery = ({
	objectType = "deployment",
	nameKey = "deployment_deviceID",
}: Props) => {
	const [searchParams, setSearchParams] = useSearchParams();
	const [formKeys, setFormKeys] = useState<String[]>([]);
	const [pageNum, setPageNum] = useState(searchParams.get("page") || 1);
	const { authTokens, user } = useContext(AuthContext);

	const checkSearchParameters = function () {
		let searchParamsObject = Object.fromEntries(searchParams);
		if (formKeys) {
			Object.entries(searchParamsObject).forEach(([key, value]) => {
				if (!formKeys.includes(key)) {
					delete searchParamsObject[key];
				}
			});
		}
		return new URLSearchParams(searchParamsObject);
	};

	const updateSearchParameters = useCallback(
		function (key, val) {
			let oldSearchParams = searchParams;
			if (oldSearchParams.size > 0) {
				oldSearchParams.set(key, val);
				setSearchParams(oldSearchParams);
			}
		},
		[searchParams, setSearchParams]
	);

	const removeSearchParameters = function (key) {
		let oldSearchParams = searchParams;
		oldSearchParams.delete(key);
		setSearchParams(oldSearchParams);
	};

	useEffect(() => {
		console.log(pageNum);
		updateSearchParameters("page", pageNum);
	}, [pageNum, updateSearchParameters]);

	const getDataFunc = async (currentSearchParams) => {
		let apiURL = `${objectType}/?${currentSearchParams.toString()}`;
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
		isPlaceholderData,
		refetch,
	} = useQuery({
		queryKey: ["data", user, checkSearchParameters().toString()],
		queryFn: () => getDataFunc(searchParams),
		enabled: searchParams.size > 0,
		placeholderData: keepPreviousData,
	});

	const onSubmit = function () {
		setPageNum(1);
	};

	const changePage = function (newPage) {
		console.log(newPage);
		setPageNum(newPage);
	};

	const openDetail = function (index) {
		updateSearchParameters("detail", index);
	};

	const closeDetail = function () {
		console.log("close detail");
		removeSearchParameters("detail");
	};

	const setEdit = function (editOn = true) {
		if (editOn) {
			updateSearchParameters("edit", editOn);
		} else {
			removeSearchParameters("edit");
		}
	};

	const addNew = function () {
		setEdit(true);
		openDetail(-1);
	};

	const showGallery = function () {
		if (isLoading || isPending) {
			return <Loading />;
		}

		if (isError) {
			return <p>An error occurred: {error.message}</p>;
		}
		if (!searchParams.get("page_size")) return;

		let maxPage = Math.ceil(data.count / Number(searchParams.get("page_size")));

		return (
			<div>
				<GalleryPageControls
					pageNum={pageNum}
					changePageCallback={changePage}
					maxPage={maxPage}
				/>
				<div
					id="display-container"
					className={isPlaceholderData ? "opacity-50" : ""}
				>
					<GalleryDisplay
						data={data.results}
						onTileClick={openDetail}
					/>
				</div>
			</div>
		);
	};

	const onDetailSubmit = function (e, addNewBool, response) {
		if (!addNewBool) {
			//let detailNum = searchParams.get("detail");
			//data.results[detailNum] = response;
			refetch();
			setEdit(false);
		} else if (addNewBool) {
			updateSearchParameters("ordering", "-created_on");
			setEdit(false);
			closeDetail();
			setPageNum(1);
			refetch();
		}
	};

	const newDELETE = async function (objID) {
		let response_json = await deleteData(
			`${nameKey}/${objID}`,
			authTokens.access
		);
		return response_json;
	};

	const doDelete = useMutation({
		mutationFn: (objID) => newDELETE(objID),
	});

	const deleteItem = async function (objID) {
		let response = await doDelete.mutateAsync(objID);
		console.log(response);
		if (response["ok"]) {
			toast(`Deleted ${objID}`);
			setPageNum(1);
			refetch();
			closeDetail();
		}
	};

	const showDetailModal = function () {
		//console.log(searchParams.get("detail") && data !== undefined);
		let modalShow = searchParams.get("detail") && data;
		if (!modalShow) {
			return null;
		}
		let detailNum = Number(searchParams.get("detail"));
		let selectedData = null;

		let maxPage;
		let maxData;

		if (detailNum !== null) {
			selectedData = data.results[detailNum];
			maxPage = Math.ceil(data.count / Number(searchParams.get("page_size")));
			maxData = data.results.length;
		} else {
			maxPage = null;
			maxData = null;
		}
		let editMode = searchParams.get("edit") || false;

		console.log(selectedData);
		return (
			<Modal
				modalShow={modalShow}
				onClose={closeDetail}
				headerChildren={
					<DetailModalHeader
						detailNum={detailNum}
						pageNum={pageNum}
						maxPage={maxPage}
						maxDetail={maxData}
						handleDetailChange={openDetail}
						handlePageChange={changePage}
						isLoading={isLoading || isPlaceholderData}
						editMode={editMode}
						canEdit={selectedData ? true : false}
						canDelete={selectedData ? true : false}
						handleEdit={setEdit}
						handleDelete={
							selectedData
								? () => {
										deleteItem(selectedData["id"]);
								  }
								: () => {}
						}
					>
						{selectedData ? selectedData[nameKey] : `Add new ${objectType}`}
					</DetailModalHeader>
				}
			>
				{editMode ? (
					<DeploymentDetailEdit
						selectedData={selectedData}
						onSubmit={onDetailSubmit}
						onCancel={
							detailNum && detailNum > -1
								? (e) => {
										setEdit(false);
								  }
								: (e) => {
										setEdit(false);
										closeDetail();
								  }
						}
					/>
				) : (
					<DetailDisplay selectedData={selectedData} />
				)}
			</Modal>
		);
	};

	return (
		<div className="container-lg">
			<div>
				{showDetailModal()}
				<GalleryForm
					onSubmit={onSubmit}
					setFormKeys={setFormKeys}
					addNew={addNew}
					nameKey={nameKey}
				/>
				{showGallery()}
			</div>
		</div>
	);
};

export default Gallery;
