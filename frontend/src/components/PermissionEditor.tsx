import React from "react";
import UserSelectorModal from "./UserSelectorModal.tsx";

interface Props {
	permissions?:
		| {
				permissionName: string;
				permissionUsers: number[];
				onPermissionChange: () => void;
		  }[]
		| [];
}

const PermissionEditor = ({ permissions = [] }: Props) => {
	return (
		<>
			{permissions.map((permission) => {
				return (
					<UserSelectorModal
						permissionname={permission.permissionName}
						chosenUsers={permission.permissionUsers}
						onPermissionChange={permission.onPermissionChange}
					/>
				);
			})}
		</>
	);
};

export default PermissionEditor;
