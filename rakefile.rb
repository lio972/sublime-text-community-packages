HERE = File.expand_path(File.dirname(__FILE__)) + '/'

require 'rake'
require 'rake/clean'
require 'fileutils'

if ENV['COMPUTERNAME'] == 'STRAWBERRY'
  ENV['HOME'] = "C:\\cygwin\\home\\atomic"
end

task :default => ['test:units', :build_packages, :build_pages]
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

desc "Commit changes to GoogleCode project"
task :push_update do
  cd HERE do
    sh "svn ci -m\"Auto updated packages via CI\""
  end
end
