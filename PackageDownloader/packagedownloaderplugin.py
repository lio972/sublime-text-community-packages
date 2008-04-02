import sublime, sublimeplugin, packagedownloader

class DownloadPackagesOnSublimeTextWikiCommand(sublimeplugin.ApplicationCommand):
  
  name = "Package Downloader"
  
  def run(self, args):
    packageList = packagedownloader.downloadPackages()
    if len(packageList) == 0:
      sublime.messageBox("No Packages Downloaded")
    else:
      sublime.messageBox("Downloaded these packages;\n\n  " + str.join("\n  ", packageList) + "\n\nPackages will be installed next time you start Sublime Text.")
