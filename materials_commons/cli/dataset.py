import json
import requests
import sys

import materials_commons.api as mcapi
from ..api import __api as mc_raw_api
from materials_commons.cli.list_objects import ListObjects
import materials_commons.cli.functions as clifuncs


class DatasetSubcommand(ListObjects):

    desc = """List, create, publish, and download datasets. By default lists all public datasets at remote. With `--proj` lists private and public datasets for the current project."""

    def __init__(self):
        super(DatasetSubcommand, self).__init__(
            ["dataset"], "Dataset", "Datasets", desc=self.desc,
            requires_project=False, non_proj_member=True, proj_member=True, expt_member=False,
            remote_help='Remote to get datasets from',
            list_columns=['name', 'owner', 'id', 'mtime', 'zip_size', 'published'],
            deletable=True,
            creatable=True,
            custom_selection_actions=['down', 'unpublish', 'publish', 'publish_private'],
            request_confirmation_actions={
                'publish': 'Are you sure you want to publicly publish these datasets?',
                'unpublish': 'Are you sure you want to unpublish these datasets?',
                'publish_private': 'Are you sure you want to privately publish these datasets?'
            }
        )

    def get_all_from_experiment(self, expt):
        return mcapi.get_all_datasets_from_experiment(expt.project.id, expt.id, expt.project.remote)

    def get_all_from_project(self, proj):
        return mcapi.get_all_datasets_from_project(proj.id, proj.remote)

    def get_all_from_remote(self, remote):
        return mcapi.get_all_datasets_from_remote(remote)

    def list_data(self, obj):

        zip_size = '-'
        if isinstance(obj, dict):
            if 'zip' in obj and 'size' in obj['zip']:
                zip_size = clifuncs.humanize(obj['zip']['size'])
        else:
            if obj.zip_status.size:
                zip_size = clifuncs.humanize(obj.zip_status.size)

        published = "no"
        if isinstance(obj, dict):
            if 'published' in obj and obj['published']:
                published = "public"
            if 'is_published_private' in obj and obj['is_published_private']:
                published = "private"
        else:
            if 'published' in obj.input_data and obj.input_data['published']:
                published = "public"
            if 'is_published_private' in obj.input_data and obj.input_data['is_published_private']:
                published = "private"

        return {
            'name': clifuncs.trunc(clifuncs.getit(obj, 'title', '-'), 40),
            'owner': clifuncs.trunc(clifuncs.getit(obj, 'owner', '-'), 40),
            'id': clifuncs.trunc(clifuncs.getit(obj, 'id', '-'), 40),
            'mtime': clifuncs.format_time(clifuncs.getit(obj, 'mtime', '-')),
            'zip_size': zip_size,
            'published': published
        }

    def print_details(self, obj, out=sys.stdout):
        if hasattr(obj, 'pretty_print'):
            obj.pretty_print(shift=0, indent=2, out=out)
        else:
            out.write(json.dumps(obj, indent=2))

    def add_custom_options(self, parser):

        # for --create, add dataset description
        parser.add_argument('--desc', type=str, default="", help='Dataset description')

        parser.add_argument('--down', action="store_true", default=False, help='Download dataset zipfile')
        parser.add_argument('--unpublish', action="store_true", default=False, help='Unpublish a dataset')
        parser.add_argument('--publish', action="store_true", default=False, help='Publish a public dataset. Makes it available for public download.')
        parser.add_argument('--publish-private', action="store_true", default=False, help='Publish a private dataset. Makes it available for globus download by project collaborators.')



    def down(self, objects, args, out=sys.stdout):
        """Download dataset zipfile, --down

        .. note:: The downloaded dataset is named <dataset_id>.zip
        """
        for obj in objects:
            out.write("Title: " + obj['title'] + "\n")
            out.write("ID: " + obj['id'] + "\n")
            out.write("Downloading...\n")
            mcapi.download_dataset_zipfile(obj['id'], obj['id']+".zip", proj.remote)
            out.write("DONE\n\n")
        return

    def create(self, args, out=sys.stdout):
        """Create new dataset

        Using `mc dataset <dataset_name> [--desc <dataset description>]
        """
        proj = clifuncs.make_local_project()

        if len(args.expr) != 1:
            print('create one dataset at a time')
            print('example: mc dataset DatasetName --create --desc "dataset description"')
            parser.print_help()
            exit(1)

        resulting_objects = []
        for name in args.expr:
            dataset = mcapi.create_dataset(proj.id, name, description=args.desc, remote=proj.remote)
            print('Created dataset:', dataset.id)
            resulting_objects.append(dataset)
        self.output(resulting_objects, args, out=out)
        return

    def delete(self, objects, args, dry_run, out=sys.stdout):
        """Delete datasets

        Using:
            mc dataset --id <dataset_id> --proj --delete
            mc dataset <dataset_name_search> --proj --delete
        """
        if dry_run:
            out.write('Dry-run is not yet possible when deleting datasets.\n')
            out.write('Aborting\n')
            return

        proj = clifuncs.make_local_project()

        for obj in objects:
            try:
                mcapi.delete_dataset(proj.id, obj.id, remote=proj.remote)
            except requests.exceptions.HTTPError as e:
                try:
                    print(e.response.json()["error"])
                except:
                    print("  FAILED, for unknown reason")
                return False
        return

    def unpublish(self, objects, args, out=sys.stdout):
        """Unpublish dataset

        Using:
            mc dataset --id <dataset_id> --proj --unpublish
            mc dataset <dataset_name_search> --proj --unpublish
        """
        proj = clifuncs.make_local_project()

        resulting_objects = []
        for obj in objects:
            try:
                # current situation is private datasets get returned after unpublishing
                # but public datasets return nothing
                res = mcapi.unpublish_dataset(proj.id, obj.id, proj.remote)
                if not res:
                    res = mcapi.get_dataset(proj.id, obj.id, proj.remote)
                resulting_objects.append(res)
            except requests.exceptions.HTTPError as e:
                try:
                    print(e.response.json()["error"])
                except:
                    print("  FAILED, for unknown reason")
                return False
        self.output(resulting_objects, args, out=out)
        return

    def publish(self, objects, args, out=sys.stdout):
        """Publish public dataset

        Using:
            mc dataset --id <dataset_id> --proj --publish
            mc dataset <dataset_name_search> --proj --publish
        """
        proj = clifuncs.make_local_project()

        resulting_objects = []
        for obj in objects:
            try:
                resulting_objects.append(mcapi.publish_dataset(proj.id, obj.id, proj.remote))
            except requests.exceptions.HTTPError as e:
                try:
                    print(e.response.json()["error"])
                except:
                    print("  FAILED, for unknown reason")
                return False
        self.output(resulting_objects, args, out=out)
        return

    def publish_private(self, objects, args, out=sys.stdout):
        """Publish private dataset

        Using:
            mc dataset --id <dataset_id> --proj --publish-private
            mc dataset <dataset_name_search> --proj --publish-private
        """
        proj = clifuncs.make_local_project()

        resulting_objects = []
        for obj in objects:
            try:
                resulting_objects.append(mcapi.publish_private_dataset(proj.id, obj.id, proj.remote))
            except requests.exceptions.HTTPError as e:
                try:
                    print(e.response.json()["error"])
                except:
                    print("  FAILED, for unknown reason")
                return False
        self.output(resulting_objects, args, out=out)
        return
