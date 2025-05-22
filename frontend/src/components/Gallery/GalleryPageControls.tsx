import React from "react";
import "../../styles/pagination.css";
import FormSelect from "../Forms/FormSelect.tsx";

interface Props {
	pageNum: number;
	maxPage: number;
	pageSize: number;
	orderBy: string;
	orderingChoices: any;
	tableMode: boolean;
	handleChangePage: (number) => void;
	handleChangeOrdering: (string) => void;
	handleChangePageSize: (string) => void;
	handleChangeTableDisplay: (bool) => void;
}

const GalleryPageControls = ({
	pageNum,
	maxPage,
	pageSize,
	orderBy,
	orderingChoices,
	tableMode,
	handleChangePage,
	handleChangeOrdering,
	handleChangePageSize,
	handleChangeTableDisplay,
}: Props) => {
	const changePage = function (change) {
		let newPage = Number(pageNum) + change;
		setPage(newPage);
	};

	const setPage = function (newPage) {
		if (newPage >= 1 && newPage <= Number(maxPage)) {
			handleChangePage(newPage);
		} else if (newPage < 1) {
			newPage = 1;
		} else if (newPage > Number(maxPage)) {
			newPage = maxPage;
		}
		return newPage;
	};

	const handlePageNum = function (e) {
		setPage(e.target.value);
	};

	const getEnabled = function (left = true) {
		if (left) {
			if (pageNum <= 1) {
				return "btn-outline-dark disabled";
			} else {
				return "";
			}
		} else {
			if (pageNum >= maxPage) {
				return "btn-outline-dark disabled";
			} else {
				return "";
			}
		}
	};

	return (
		<div
			id="page-controls"
			className="row gallery-page-controls justify-content-center"
		>
			<div className="col row col-12 col-lg-4 py-1 py-lg-0 order-lg-1">
				<div className="col col-6 table-control">
					<div className="form-check form-switch">
						<label htmlFor="set-tablemode">Table view</label>
						<input
							name="autoupdate"
							className="form-check-input form-control"
							id="set-tablemode"
							checked={tableMode}
							type="checkbox"
							onChange={(e) => {
								handleChangeTableDisplay(e.target.checked);
							}}
						/>
					</div>
				</div>
				<div className="col col-6">
					<div className="input-group input-group-sm h-100">
						<span className="input-group-text">Items per page: </span>
						<input
							className="form-control"
							name="page_size"
							type="number"
							min="1"
							max="100"
							step="5"
							value={pageSize}
							onChange={(e) => {
								setPage(1);
								handleChangePageSize(e.target.value);
							}}
						/>
					</div>
				</div>
			</div>
			<div className="col col-lg-4 py-1 py-lg-0 order-lg-3">
				<div className="input-group input-group-sm">
					<span className="input-group-text">Order by: </span>
					<FormSelect
						id="select-ordering"
						name="ordering"
						label="Order by"
						choices={orderingChoices}
						isSearchable={false}
						isClearable={false}
						//defaultvalue={searchParams.get("is_active") || null}
						value={orderBy}
						handleChange={handleChangeOrdering}
					/>
				</div>
			</div>
			<div className="col-12 col-lg-4 row justify-content-center gx-0 py-1 py-lg-0 order-lg-2 px-3">
				<div className="col col-lg-auto">
					<button
						className={`btn btn-outline-primary button-left ${getEnabled(
							true
						)}`}
						aria-label="Previous"
						onClick={(e) => changePage(-1)}
					>
						<span aria-hidden="true">&laquo;</span>
					</button>
				</div>
				<div className="col-auto">
					<input
						name="pagination-page"
						className="page-input h-100"
						type="number"
						min="1"
						value={pageNum}
						onChange={handlePageNum}
					/>
				</div>
				<div className="page-description col-auto">
					<div className="align-middle page-count">of {maxPage}</div>
				</div>
				<div className="col col-lg-auto">
					<button
						className={`btn btn-outline-primary button-right ${getEnabled(
							false
						)}`}
						aria-label="Next"
						onClick={(e) => changePage(1)}
					>
						<span aria-hidden="true">&raquo;</span>
					</button>
				</div>
			</div>
		</div>
	);
};

export default GalleryPageControls;
