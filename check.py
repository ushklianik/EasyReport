from app.backend.integrations.atlassian.wiki import wiki

obj = wiki("default", "conflwiki")
page = obj.confl.get_page_by_id("17105117", expand="body.storage")
print(page['body']['storage']['value'])