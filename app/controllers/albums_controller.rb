class AlbumsController < ApplicationController
    def show
        @host = 'https://pc.animelo.jp'
        if params[:id].eql? '-1'
            render 'notf'
        else
            @album = Album.find(params[:id])
        end
    end

    def query
        url = params[:album][:url]
        if url =~ /^((ht|f)tps?):\/\/[\w\-]+(\.[\w\-]+)+([\w\-.,@?^=%&:\/~+#]*[\w\-@?^=%&\/~+#])?$/
            id = `python query.py "#{url}"`.strip
        else
            id = -1
        end
        redirect_to :action=>'show', :id=>id

        # RubyPython.start
        # sys = RubyPython.import('sys')
        # require 'shell'
        # cwd = Shell.new.cwd
        # sys.path.append(cwd)
        # pyquery = RubyPython.import('query')
        # sys.path.remove(cwd)
        # id = pyquery.query(url)
        # RubyPython.stop
    end

    def notf
    end
end
# test case: http://imgsrc.baidu.com/forum/pic/item/4d5d6b2d11dfa9ecca3e84816ad0f703908fc1a0.jpg
# test case: http://imgsrc.baidu.com/forum/pic/item/4f1ad7bf6c81800a24601013bb3533fa838b47ec.jpg