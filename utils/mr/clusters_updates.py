import ruamel.yaml as yaml

from utils.mr.base import MergeRequestBase
from utils.mr.labels import AUTO_MERGE
from utils.mr.labels import SKIP_CI


class CreateClustersUpdates(MergeRequestBase):

    name = 'create_clusters_updates_mr'

    def __init__(self, clusters_updates):
        self.clusters_updates = clusters_updates

        super().__init__()

        self.labels = [AUTO_MERGE, SKIP_CI]

    @property
    def title(self):
        return (f'[{self.name}] clusters updates')

    def process(self, gitlab_cli):
        for cluster_name, cluster_updates in self.clusters_updates.items():
            if not cluster_updates:
                continue

            cluster_path = cluster_updates.pop('path')
            raw_file = gitlab_cli.project.files.get(file_path=cluster_path,
                                                    ref=self.main_branch)
            content = yaml.load(raw_file.decode(), Loader=yaml.RoundTripLoader)
            if 'spec' not in content:
                self.cancel('Spec missing. Nothing to do.')

            # if we are here, it means that there are updates
            content['spec'].update(cluster_updates)

            new_content = '---\n'
            new_content += yaml.dump(content, Dumper=yaml.RoundTripDumper)

            msg = f'update cluster {cluster_name} spec fields'
            gitlab_cli.update_file(branch_name=self.branch,
                                   file_path=cluster_path,
                                   commit_message=msg,
                                   content=new_content)