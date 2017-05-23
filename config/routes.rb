Rails.application.routes.draw do
    root 'welcome#index'

    post '/', :to=>'albums#query'
    get '/album/:id', :to=>'albums#show'
end
