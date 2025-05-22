import React, { ReactElement } from "react";
import "../../styles/detailmodal.css";

interface Props {
	modalId?: string;
	modalShow?: boolean;
	children?: ReactElement;
	headerChildren?: ReactElement | string;
	onClose?: () => void;
	className?: string;
}

const BasicModal = ({
	modalId = "",
	modalShow = false,
	children,
	headerChildren = "",
	onClose = () => {},
	className = "",
}: Props) => {
	//$el.scrollTo({top: 0, behavior: 'instant'}

	const onBackGroundClick = function (e) {
		if (e.currentTarget !== e.target) return;
		onClose();
	};

	const getHeader = function () {
		if (typeof headerChildren == "string") {
			return <div className="modal-header">{headerChildren}</div>;
		} else {
			return headerChildren;
		}
	};

	const showModal = function () {
		if (modalShow) {
			return (
				<div
					id={modalId}
					className="modal"
					role="dialog"
					onClick={onBackGroundClick}
				>
					<div className={`modal-dialog ${className}`}>
						<div className="modal-content shadow">
							{getHeader()}
							<div className="modal-body py-1">{children}</div>
						</div>
					</div>
				</div>
			);
		} else {
			return null;
		}
	};

	return showModal();
};

export default BasicModal;
