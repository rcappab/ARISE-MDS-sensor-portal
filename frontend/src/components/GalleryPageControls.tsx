import React from "react";
import "../styles/pagination.css";
import { useState } from "react";
import Loading from "./Loading.jsx";

const GalleryPageControls = (props) => {
	const changePage = function (change) {
		console.log("new page");
		let newPage = Number(props.pageNum) + change;
		newPage = setPage(newPage);
	};

	const setPage = function (newPage) {
		console.log("set page");
		console.log(newPage);
		if (newPage >= 1 && newPage <= Number(props.maxPage)) {
			props.changePageCallback(newPage);
		} else if (newPage < 1) {
			newPage = 1;
		} else if (newPage > Number(props.maxPage)) {
			newPage = props.maxPage;
		}
		return newPage;
	};

	const handlePageNum = function (e) {
		let newPage = setPage(e.target.value);
	};

	const getEnabled = function (left = true) {
		if (left) {
			if (props.pageNum <= 1) {
				return "btn-outline-dark disabled";
			} else {
				return "";
			}
		} else {
			if (props.pageNum >= props.maxPage) {
				return "btn-outline-dark disabled";
			} else {
				return "";
			}
		}
	};

	return (
		<div id="page-controls">
			<nav aria-label="Page navigation">
				<ul className="pagination justify-content-center">
					<li className="page-item">
						<a
							className={`btn btn-outline-primary button-left ${getEnabled(
								true
							)}`}
							aria-label="Previous"
							onClick={(e) => changePage(-1)}
						>
							<span aria-hidden="true">&laquo;</span>
						</a>
					</li>
					<li className="page-item">
						<input
							name="pagination-page"
							className="page-input"
							type="number"
							min="1"
							value={props.pageNum}
							onChange={handlePageNum}
						/>
					</li>
					<li className="page-item page-description">
						<div className="text-center align-middle page-count">
							{props.maxPage}
						</div>
					</li>
					<li className="page-item">
						<a
							className={`btn btn-outline-primary button-right ${getEnabled(
								false
							)}`}
							aria-label="Next"
							onClick={(e) => changePage(1)}
						>
							<span aria-hidden="true">&raquo;</span>
						</a>
					</li>
				</ul>
			</nav>
		</div>
	);
};

export default GalleryPageControls;
