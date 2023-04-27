/**
 * take update from client for new location target
 */
take_target_location_update(message_data)
{
    if(message_data.value == "success")
    {
        app.session.world_state.session_players[message_data.session_player_id].target_location = message_data.target_location;        
        app.send_world_state_update()         
    } 
    else
    {
        
    }
},

/**
 * send an update to the server to store the current world state
 */
send_world_state_update(){
    if(app.last_world_state_update == null) 
    {
        app.last_world_state_update = Date.now();
        return;
    }

    if(Date.now() - app.last_world_state_update < 1000) return;

    let temp_world_state = {"session_players":{}}

    for(i in app.session.world_state.session_players)
    {
        temp_world_state["session_players"][i] = {"current_location" : app.session.world_state.session_players[i].current_location};
    }

    app.last_world_state_update = Date.now();
    app.send_message("world_state_update", {"world_state" : temp_world_state});       
},


take_update_collect_token(message_data){

    let token = app.session.world_state.tokens[message_data.period_id][message_data.token_id];

    token.token_container.getChildAt(0).stop();
    token.token_container.getChildAt(0).alpha = 0.25;
    token.status = message_data.player_id;

    let session_player = app.session.world_state.session_players[message_data.player_id];
    session_player.inventory[message_data.period_id] = message_data.inventory;
    session_player.pixi.avatar_container.getChildAt(4).text = message_data.inventory;
},