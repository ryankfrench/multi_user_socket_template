
import logging

from asgiref.sync import sync_to_async

from django.db import transaction
from django.db.models.fields.json import KT

from main.models import SessionPlayer
from main.models import Session

from datetime import datetime, timedelta

class SubjectUpdatesMixin():
    '''
    subject updates mixin for staff session consumer
    '''

    async def update_chat(self, event):
        '''
        send chat to clients, if clients can view it
        '''
        event_data = event["staff_data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_connection_status(self, event):
        '''
        handle connection status update from group member
        '''
        event_data = event["data"]

        #update not from a client
        if event_data["value"] == "fail":
            return
        
        subject_id = event_data["result"]["id"]

        session_player = await SessionPlayer.objects.aget(id=subject_id)
        event_data["result"]["name"] = session_player.name
        event_data["result"]["student_id"] = session_player.student_id
        event_data["result"]["current_instruction"] = session_player.current_instruction
        event_data["result"]["survey_complete"] = session_player.survey_complete
        event_data["result"]["instructions_finished"] = session_player.instructions_finished

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_name(self, event):
        '''
        send update name notice to staff screens
        '''

        event_data = event["staff_data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_next_instruction(self, event):
        '''
        send instruction status to staff
        '''

        event_data = event["staff_data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def update_finish_instructions(self, event):
        '''
        send instruction status to staff
        '''

        event_data = event["staff_data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def update_survey_complete(self, event):
        '''
        send survey complete update
        '''
        event_data = event["data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def target_location_update(self, event):
        '''
        update target location from subject screen
        '''
        logger = logging.getLogger(__name__)
        
        event_data =  event["message_text"]

        try:
            target_location = event_data["target_location"]            
        except KeyError:
            return
            # result = {"value" : "fail", "result" : {"message" : "Invalid location."}}
        
        player_id = self.session_players_local[event["player_key"]]["id"]
        session_player = self.world_state_local["session_players"][str(player_id)]

        if session_player["frozen"] or session_player["tractor_beam_target"]:
            return

        session_player["target_location"] = target_location

        last_update = datetime.strptime(self.world_state_local["last_update"], "%Y-%m-%d %H:%M:%S.%f")
        dt_now = datetime.now()

        if dt_now - last_update > timedelta(seconds=1):
            # logger.info("updating world state")
            self.world_state_local["last_update"] = str(dt_now)
            await Session.objects.filter(id=self.session_id).aupdate(world_state=self.world_state_local)
        
        result = {"value" : "success", "target_location" : target_location, "session_player_id" : player_id}
        
        await self.send_message(message_to_self=None, message_to_group=result,
                                message_type=event['type'], send_to_client=False, send_to_group=True)

    async def update_target_location_update(self, event):
        '''
        update target location from subject screen
        '''

        event_data = event["group_data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

        
    
    async def collect_token(self, event):
        '''
        subject collects token
        '''
        logger = logging.getLogger(__name__)
        
        message_text = event["message_text"]
        token_id = message_text["token_id"]
        period_id = message_text["period_id"]
        player_id = self.session_players_local[event["player_key"]]["id"]

        if not await sync_to_async(sync_collect_token)(self.session_id, period_id, token_id, player_id):
            logger.warning(f'collect_token: {message_text}, token {token_id} not available')
            return
        
        self.world_state_local['tokens'][str(period_id)][str(token_id)]['status'] = player_id
        self.world_state_local['session_players'][str(player_id)]['inventory'][str(period_id)]+=1

        inventory = self.world_state_local['session_players'][str(player_id)]['inventory'][str(period_id)]

        await Session.objects.filter(id=self.session_id).aupdate(world_state=self.world_state_local)

        result = {"token_id" : token_id, "period_id" : period_id, "player_id" : player_id, "inventory" : inventory}

        #logger.warning(f'collect_token: {message_text}, token {token_id}')

        await self.send_message(message_to_self=None, message_to_group=result,
                                message_type=event['type'], send_to_client=False, send_to_group=True)


    async def update_collect_token(self, event):
        '''
        subject collects token update
        '''
        event_data = event["group_data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def tractor_beam(self, event):
        '''
        subject activates tractor beam
        '''

        player_id = self.session_players_local[event["player_key"]]["id"]
        target_player_id = event["message_text"]["target_player_id"]

        source_player = self.world_state_local['session_players'][str(player_id)]
        target_player = self.world_state_local['session_players'][str(target_player_id)]

        # check if players are frozen
        if source_player['frozen'] or target_player['frozen']:
            return

        #check if either player has tractor beam enabled
        if source_player['tractor_beam_target'] or target_player['tractor_beam_target']:
            return
        
        #check if player is already interacting or cooling down.
        if source_player['interaction'] > 0 or source_player['cool_down'] > 0:
            return
        
        source_player['frozen'] = True
        target_player['frozen'] = True

        source_player['tractor_beam_target'] = target_player_id
        source_player['interaction'] = self.parameter_set_local['interaction_length']

        target_player['interaction'] = self.parameter_set_local['interaction_length']

        await Session.objects.filter(id=self.session_id).aupdate(world_state=self.world_state_local)

        result = {"player_id" : player_id, "target_player_id" : target_player_id}
        
        await self.send_message(message_to_self=None, message_to_group=result,
                                message_type=event['type'], send_to_client=False, send_to_group=True)

    async def update_tractor_beam(self, event):
        '''
        subject activates tractor beam update
        '''

        event_data = event["group_data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
        
    async def interaction(self, event):
        '''
        subject sends an interaction
        '''
        player_id = self.session_players_local[event["player_key"]]["id"]

        source_player = self.world_state_local['session_players'][str(player_id)]

        if source_player['interaction'] == 0:
            return
        
        target_player_id = source_player['tractor_beam_target']
        target_player = self.world_state_local['session_players'][str(target_player_id)]


        #clear status
        source_player['interaction'] = 0
        target_player['interaction'] = 0

        source_player['frozen'] = False
        target_player['frozen'] = False

        source_player["cool_down"] = self.parameter_set_local["cool_down_length"]
        target_player["cool_down"] = self.parameter_set_local["cool_down_length"]

        source_player['tractor_beam_target'] = None

        result = {"source_player_id": player_id, "value" : "success"}
        
        await self.send_message(message_to_self=None, message_to_group=result,
                                message_type=event['type'], send_to_client=False, send_to_group=True)

    async def update_interaction(self, event):
        '''
        subject send an interaction update
        '''

        event_data = event["group_data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def cancel_interaction(self, event):
        '''
        subject transfers tokens
        '''
        player_id = self.session_players_local[event["player_key"]]["id"]

        source_player = self.world_state_local['session_players'][str(player_id)]

        if source_player['interaction'] == 0:
            return
        
        target_player_id = source_player['tractor_beam_target']
        target_player = self.world_state_local['session_players'][str(target_player_id)]

        source_player['interaction'] = 0
        target_player['interaction'] = 0

        source_player['frozen'] = False
        target_player['frozen'] = False

        source_player['tractor_beam_target'] = None

        await Session.objects.filter(id=self.session_id).aupdate(world_state=self.world_state_local)

        result = {"source_player_id" : player_id, "target_player_id" : target_player_id, "value" : "success"}
        
        await self.send_message(message_to_self=None, message_to_group=result,
                                message_type=event['type'], send_to_client=False, send_to_group=True)

    async def update_cancel_interaction(self, event):
        '''
        subject transfers tokens update
        '''
        event_data = event["group_data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
        

#sync companion functions
def sync_collect_token(session_id, period_id, token_id, player_id):
    '''
    syncronous collect token transaction
    '''

    # world_state_filter=f"world_state__tokens__{period_id}__{token_id}__status"
    
    with transaction.atomic():
    
        session = Session.objects.select_for_update().get(id=session_id)

        if session.world_state['tokens'][str(period_id)][str(token_id)]['status'] != 'available':
            return False

        session.world_state['tokens'][str(period_id)][str(token_id)]['status'] = 'waiting'
        session.save()

    return True

def sync_interaction(session_id, source_player_id, target_player_id, direction, amount):
    '''
    syncronous interaction transaction
    '''

    # world_state_filter=f"world_state__tokens__{period_id}__{token_id}__status"
    
    with transaction.atomic():
    
        session = Session.objects.select_for_update().get(id=session_id)

        source_player = session.world_state['session_players'][str(source_player_id)]
        target_player = session.world_state['session_players'][str(target_player_id)]

        if direction == 'take':
            if target_player["inventory"] < amount:
                return False
            else:
                target_player["inventory"] -= amount
                source_player["inventory"] += amount
        else:
            if source_player["inventory"] < amount:
                return False
            else:
                source_player["inventory"] -= amount
                target_player["inventory"] += amount
                
        session.save()

    return True
                                      
    

                                
        

