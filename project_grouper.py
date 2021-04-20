"""
Adds tasks in configured projects to other configured projects
"""

from lib import Client

# To get it on a list run this on herald rule page
# const items = document.getElementsByClassName('herald-list-item')[0].getElementsByClassName('phui-handle')
# for (i in items) {console.log(items[i].text)};
rules = [
    {
        # H175 - see T136921
        'add': 'Design',
        'in': ['WMF-Design', 'WMDE-Design'],
    },
    {
        # H232
        'add': 'artificial-intelligence',
        'in': ['editquality-modeling', 'draftquality-modeling', 'articlequality-modeling', 'revscoring'],
    },
    {
        # H193 - see T146701
        'add': 'accessibility',
        'in': ['ios-app-feature-accessibility'],
    },
    {
        # H174
        'add': 'upstream',
        'in': ['phabricator-upstream'],
    },
    {
        # H24 - see T86536
        'add': 'universallanguageselector',
        'in': ['uls-compactlinks'],
    },
    {
        # H15 - note that #producrement tasks are private -> rule can't be disabled
        'add': 'Operations',
        'in': [
            'ops-eqiad',
            'ops-codfw',
            'ops-esams',
            'ops-ulsfo',
            # 'hardware-requests', archived project
            'SRE-Access-Requests',
            'netops',
            'vm-requests',
            'Traffic',
            'ops-eqord',
            'ops-eqdfw',
            # 'procurement', always in S4
            'ops-eqsin',
            'DNS',
            'LDAP-Access-Requests',
            'Wikimedia-Mailing-lists',
        ],
    },
    {
        # H14 - see T85596
        'add': 'Social-Tools',
        'in': [
            'BlogPage',
            'Comments',
            'FanBoxes',
            'LinkFilter',
            'PollNY',
            'QuizGame',
            # 'RandomFeaturedUser', archived project
            'RandomGameUnit',
            'SocialProfile',
            'SiteMetrics',
            'VoteNY',
            'WikiForum',
            'WikiTextLoggedInOut',
            'Challenge',
            'MiniInvite',
            # 'NewUsersList', archived project
            'PictureGame',
            # 'RandomUsersWithAvatars', archived project
            'video_non-wmf',
            # 'TopLists', archived project
        ],
    },
    {
        # H10 - see T76954
        'add': 'VisualEditor',
        'in': [
            'VisualEditor-ContentEditable',
            'VisualEditor-ContentLanguage',
            'VisualEditor-CopyPaste',
            'VisualEditor-DataModel',
            'VisualEditor-EditingTools',
            'VisualEditor-Initialisation',
            'VisualEditor-InterfaceLanguage',
            'VisualEditor-MediaWiki',
            'VisualEditor-MediaWiki-Links',
            'VisualEditor-MediaWiki-Media',
            'VisualEditor-MediaWiki-Mobile',
            'VisualEditor-MediaWiki-References',
            'VisualEditor-MediaWiki-Templates',
            'VisualEditor-Performance',
            'VisualEditor-Tables',
            'TemplateData',
            'VisualEditor-MediaWiki-Plugins',
            'VisualEditor-LanguageTool',
            'VisualEditor-Links',
            'VisualEditor-Media',
            'VisualEditor-MediaWiki-2017WikitextEditor',
            'VisualEditor-VisualDiffs',
        ],
    },
    {
        # T280119
        'add': 'observability',
        'in': [
            'wikimedia-logstash',
            'icinga',
            'graphite',
        ],
    },
    {
        'add': 'user-urbanecm-wmf-engineering',
        'in': [
            'growth-deployments',
        ]
    },
    {
        # H30
        'add': 'wikidata',
        'in': [
            'Wikidata-Page-Banner',
            'Wikibase-Quality-Constraints',
            'DataValues',
            'DataValues-JavaScript',
            'MediaWiki-extensions-WikibaseClient',
            'MediaWiki-extensions-WikibaseView',
            'Wikibase-DataModel',
            'Wikibase-DataModel-JavaScript',
            'Wikibase-DataModel-Serialization',
            'Wikibase-Internal-Serialization',
            'Wikibase-JavaScript-Api',
            'Wikibase-Serialization-JavaScript',
            'Wikidata-Query-Service',
            'Tool-Wikidata-Periodic-Table',
            'Wikidata.org',
            'DataTypes',
            'MediaWiki-extensions-WikibaseRepository',
            'SDC General',
            'ValueView',
            'Wikidata-Gadgets',
            'ArticlePlaceholder',
            'Wikidata Lexicographical data',
            'Automated list generation',
            'Wikidata Query UI',
            'Wikibase-Containers',
            'Soweego',
            'Wikidata Mobile',
            'Wikidata-Campsite',
            'Wikibase-registry',
            'wikiba.se website',
            'Wikibase-Lua',
            'MediaWiki-extensions-PropertySuggester',
            'Wikidata-Campsite (Wikidata-Campsite-Iteration-∞)',
            'RL Module Terminators Trailblazing',
            'Wikidata-Bridge',
            'Shape Expressions',
            'Wikidata Tainted References',
            'Wikidata Design System',
            'Wikidata - Reference Treasure Hunt',
            'Item Quality Scoring Improvement',
            'Wikibase - Automated Configuration Detection (WikibaseManifest)',
            'Wikidata Query Builder',
            'Wikidata - Visualisation of Reliability Metrics'
        ],
        'once': True
    }
]

client = Client.newFromCreds()

for rule in rules:
    handled_tasks = []

    wanted_project_phid = client.lookupPhid('#' + rule['add'])
    for project_name in rule['in']:
        project_name = project_name.replace(' ', '_')
        project_phid = client.lookupPhid('#' + project_name)
        for task_phid in client.getTasksWithProject(project_phid):
            # if a task is in multiple 'in' projects, still only process it once
            if task_phid in handled_tasks:
                continue
            task = client.taskDetails(task_phid)
            if wanted_project_phid in task['projectPHIDs']:
                continue
            if rule.get('once') == True:
                is_already_added = False
                transactions = client.getTransactions(task_phid)
                for transaction in transactions:
                    operations = transaction.get(
                        'fields', {}).get('operations', [])
                    for operation in operations:
                        if operation.get('operation') == 'add' and operation.get('phid') == wanted_project_phid:
                            is_already_added = True
                            break
                if is_already_added == True:
                    continue
            handled_tasks.append(task_phid)
            client.addTaskProject(task_phid, wanted_project_phid)
