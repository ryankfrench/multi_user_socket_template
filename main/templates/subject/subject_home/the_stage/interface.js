target_location_update(){
    app.send_message("target_location_update", 
                    {"target_location" : app.session.world_state.session_players[app.session_player.id].target_location},
                    "self");                   
},

take_target_location_update(message_data){
    if(message_data.value == "success")
    {
        app.session.world_state.session_players[message_data.session_player_id].target_location = message_data.target_location;                 
    } 
    else
    {
        
    }
},

take_update_collect_token(message_data){

},
