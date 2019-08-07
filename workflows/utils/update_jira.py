import os
import logging
from jira import JIRA, JIRAError

from dbclients.colossus import ColossusApi
from dbclients.tantalus import TantalusApi

colossus_api = ColossusApi()
tantalus_api = TantalusApi()

log = logging.getLogger('sisyphus')
JIRA_USER = os.environ['JIRA_USERNAME']
JIRA_PASSWORD = os.environ['JIRA_PASSWORD']
jira_api = JIRA('https://www.bcgsc.ca/jira/', basic_auth=(JIRA_USER, JIRA_PASSWORD))

def update_jira_dlp(jira_id, aligner):
    logging.info("Updating description on {}".format(jira_id))

    description = [
        '(/) Alignment with ' + aligner,
        '(/) Hmmcopy',
        '(/) Classifier',
        '(/) Path to results on blob:',
        '{noformat}Container: singlecelldata\nresults/' + jira_id + '{noformat}',
    ]

    update_description(jira_id, description, "jbiele", remove_watcher=True)



def update_jira_tenx(jira_id, args):
    """
    Update analysis jira ticket desription with link to Tantalus result dataset and 
        Colossus library

    Args:
        jira (str): Jira ticket ID
        args (dict):
    """

    results_dataset = tantalus_api.get("resultsdataset", analysis__jira_ticket=jira_id)
    results_dataset_id = results_dataset["id"]

    library = colossus_api.get("tenxlibrary", name=args["library_id"])
    library_id = library["id"]

    description = [
        "{noformat}Storage Account: scrnadata\n {noformat}",
        "Tantalus Results: https://tantalus.canadacentral.cloudapp.azure.com/results/{}".format(
            results_dataset_id
        ),
        "Colossus Library: https://colossus.canadacentral.cloudapp.azure.com/tenx/library/{}".format(
            library_id
        ),
    ]

    update_description(jira_id, description, "coflanagan", remove_watcher=True)


def update_description(jira_id, description, assignee, remove_watcher=False):

    description = '\n\n'.join(description)
    issue = jira_api.issue(jira_id)

    issue.update(notify=False, assignee={"name": assignee}, description=description)

    # Remove self as watcher
    if remove_watcher:
        jira_api.remove_watcher(issue, JIRA_USER)


def add_attachment(jira_id, attachment_file_path, attachment_filename):
    """
    Checks if file is already added to jira ticket; attaches if not. 
    """
    issue = jira_api.issue(jira_id)
    current_attachments = [a.filename for a in issue.fields.attachment]

    if attachment_filename in current_attachments:
        log.info("{} already added to {}".format(attachment_filename, jira_id))

    else:
        log.info("Adding {} to {}".format(attachment_filename, jira_id))
        jira_api.add_attachment(issue=jira_id, attachment=attachment_file_path)

