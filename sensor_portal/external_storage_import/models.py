from django.db import models
from django.conf import settings
from utils.models import BaseModel
from encrypted_model_fields.fields import EncryptedCharField
from utils.ssh_client import SSH_client
from posixpath import join, splitext
from data_models.file_handling_functions import create_file_objects
from django.conf import settings
import io
from django.core.files import File


class DataStorageInput(BaseModel):
    name = models.CharField(max_length=20, unique=True)
    username = models.CharField(
        max_length=50, unique=True)
    password = EncryptedCharField(max_length=128)
    address = models.CharField(
        max_length=100, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name="owned_inputstorages",
                              on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def init_ssh_client(self):
        return SSH_client(self.username, self.password, self.address, 22)

    def setup_users(self):
        ssh_client = self.init_ssh_client()
        ssh_client.connect_to_ftp()

    def check_connetion(self):
        # Should try and connect to server based on provided credentials.
        pass

    def check_input(self):
        ssh_client = self.init_ssh_client()
        ssh_client.connect_to_ftp()
        all_devices = self.linked_devices.all()
        all_dirs_attributes = ssh_client.ftp_sftp.listdir_attr()
        file_names = [x.filename for x in all_dirs_attributes]
        for device in all_devices:
            print(f"{self.name} - {device.device_ID} - checking storage")
            if device.username is None:
                print(f"{self.name} - {device.device_ID} - configured incorrectly")
                continue
            # check for folder of this device
            if device.username not in file_names:
                print(
                    f"{self.name} - {device.device_ID} - not found on external storage")
                continue

            # check for files
            device_dir_attribute = ssh_client.ftp_sftp.listdir_attr(
                device.username)
            device_file_names = [
                x.filename for x in device_dir_attribute if all([y != ''for y in splitext(x.filename)])]
            if len(device_file_names) == 0:
                print(
                    f"{self.name} - {device.device_ID} - no files on external storage")
                continue

            files = []
            for filename in device_file_names:
                with ssh_client.ftp_sftp.open(join(device.username, filename), bufsize=32768) as f:
                    f.set_pipelined
                    f.prefetch()
                    f_bytes = io.BytesIO(f.read())
                    file_object = File(f_bytes, name=filename)
                    files.append(file_object)

            print(files)

            # import files
            downloaded_files, invalid_files, existing_files, status = create_file_objects(
                files, device_object=device)
            print(f"{self.name} - {device.device_ID} - {status}")

            # delete files that are succesfully downloaded
            for filename in downloaded_files:
                print(
                    f"{self.name} - {device.device_ID} -{filename} succesfully downloaded")
                if not settings.DEVMODE:
                    ssh_client.ftp_sftp.remove(join(device.username, filename))
                    print(f"{self.name} - {device.device_ID} -{filename} removed")

            for problem_file in invalid_files:
                print(
                    f"{self.name} - {device.device_ID} - {problem_file}")
        ssh_client.CloseConnectionToFTP
