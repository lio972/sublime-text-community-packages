HERE = File.expand_path(File.dirname(__FILE__)) + '/'

require 'rake'
require 'rake/clean'
require 'fileutils'

task :default => ['test:units', :build_packages, :add_files, :build_pages]
task :all => [:clobber, :default]
task :ci => [:all, :push_update]

namespace :test do

  desc "Run unit tests"
  task :units do
    cd HERE do
      puts "Need to add some tests!"
    end
  end

end

desc "Build wiki base pages"
task :build_pages do
  cd HERE do
    sh "python cgi/makePages.py"
  end
end

desc "Build SublimeText packages their pages"
task :build_packages do
  cd HERE do
    sh "python cgi/makeSublimePackages.py"
  end
end

desc "Add new files"
task :add_files do
  cd HERE do
    svn_stat = `svn st`.split("\n")[0..-1]
    svn_stat.each do |item|
      file_match = item.match(/^\?\s+(.*)$/)
      if file_match
        new_file = file_match[1]
        sh "svn add " + new_file
        if new_file =~ /\.html$/
          sh "svn propset svn:mime-type text/html " + new_file
        end
      end
    end
  end
end

desc "Commit changes to GoogleCode project"
task :push_update do
  cd HERE do
    sh "svn ci -m\"Auto updated packages via CI\""
  end
end
