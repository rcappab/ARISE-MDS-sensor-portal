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
	console.log(permissions);
	return (
		<>
			{permissions.map((permission) => {
				console.log(permission);
				return (
					<>
						<UserSelectorModal
							permissionname={permission.permissionName}
							chosenUsers={permission.permissionUsers}
							onPermissionChange={permission.onPermissionChange}
						/>
						<input
							name={`${permission.permissionName.toLowerCase()}_ID`}
							value={JSON.stringify(permission.permissionUsers)}
							hidden
						></input>
					</>
				);
			})}
		</>
	);
};

export default PermissionEditor;
