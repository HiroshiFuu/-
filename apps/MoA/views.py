from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.core import serializers

from .models import Game, ZodiacImage, Zodiac, Character, Player
from .base_model import CHARACTOR_CHOICES, COLOR_CHOICES, ZODIAC_CHOICES

from datetime import timedelta
import random
import json


def get_a_character(game):
	characters = game.characters.all()
	# character = random.choice(characters)
	character = characters.first()	# for testing
	game.characters.remove(character)
	return character


def get_all_colors():
	all_colors = sorted([color[0] for color in COLOR_CHOICES])
	# print(all_colors)
	return all_colors


# Create your views here.
def Home(request):
	return render(request, 'home.html', {})


def CreateGame(request):
	room_id = random.randint(10000, 32767)
	while Game.objects.filter(room_id=room_id).count() > 0:
		room_id = random.randint(10000, 32767)	
	new_game = Game(room_id=room_id, start_color_index=random.randint(0, 7))
	new_game.save()
	zodiac_names = [zodiac[0] for zodiac in ZODIAC_CHOICES]
	# zodiac_genuines = [True] * 6 + [False] * 6
	for i in range(12):
		if i % 4 == 0:
			zodiac_genuines = [True] * 2 + [False] * 2
		name = random.choice(zodiac_names)
		zodiac_image = ZodiacImage.objects.get(name=name)
		genuine = random.choice(zodiac_genuines)
		zodiac = Zodiac(name=name, genuine=genuine, sequence=i, zodiac_image=zodiac_image, game=new_game)
		zodiac.save()
		print(zodiac)
		new_game.zodiacs.add(zodiac)
		zodiac_names.remove(name)
		zodiac_genuines.remove(genuine)
	request.session['create_at'] = str(timezone.now())
	characters = Character.objects.all()
	for character in characters:
		new_game.characters.add(character)
	return render(request, 'to_setup.html', {'room_id': room_id})


def RecoverPlayer(request):
	player_code = request.POST.get('player_code', None)
	if player_code is None or len(player_code) != 3:
		return redirect('MoA:Home')
	player = Player.objects.filter(player_code=player_code).first()
	if player is None:
		return redirect('MoA:Home')

	request.session['player_code'] = player_code
	room_id = player.game.room_id
	game = Game.objects.filter(room_id=room_id).first()
	if game is None:
		return redirect('MoA:Home')
	if game.stage == -1:
		return render(request, 'to_setup.html', {'room_id': room_id})
	else:
		return render(request, 'to_game.html', {'room_id': room_id})


def SetupGame(request):
	room_id = request.POST.get('room_id', None)
	if room_id is None or len(room_id) != 5:
		return redirect('MoA:Home')
	game = Game.objects.filter(room_id=room_id).first()
	if game is None:
		return redirect('MoA:Home')

	player_code = request.session.get('player_code', None)
	print(player_code)

	all_colors = get_all_colors()
	if player_code is None:
		player_code = random.randint(100, 999)
		while Player.objects.filter(player_code=player_code).count() > 0:
			player_code = random.randint(100, 999)
		request.session['player_code'] = player_code
		request.session['join_at'] = str(timezone.now())
		character = get_a_character(game)
		players = game.players.all()
		player_colors = [player.color for player in players]
		available_colors = [c for c in player_colors + all_colors if c not in player_colors or c not in all_colors]
		# color = random.choice(available_colors)
		color = available_colors[0]	# for testing
		new_player = Player(player_code=player_code, color=color, game=game, character=character)
		name = new_player.get_color_display()
		new_player.name = name
		new_player.save()
		game.players.add(new_player)
	player = Player.objects.get(player_code=player_code)
	return render(request, 'setup.html', {'room_id': room_id, 'player': player, 'colors': all_colors})


def SetPlayerName(request):
	player_code = request.session.get('player_code', None)
	player = Player.objects.get(player_code=player_code)
	player.name = request.POST.get('name', None)
	player.save()
	return HttpResponse(name, status=201)


def GetConnectedPlayerColors(request):
	room_id = request.POST.get('room_id', None)
	game = Game.objects.get(room_id=room_id)
	players = game.players.all()
	player_colors = [player.color for player in players]
	return HttpResponse(json.dumps(player_colors), content_type='application/json', status=200)


def IamAlive(request):
	player_code = request.POST.get('player_code', None)
	player = Player.objects.get(player_code=player_code)
	player.save()
	return HttpResponse('alive', status=200)


def GetAlivePlayerColors(request):
	room_id = request.POST.get('room_id', None)
	game = Game.objects.get(room_id=room_id)
	if game.stage == -1:
		players = [player for player in game.players.all() if player.is_alive()]
	elif game.stage >= 0:
		players = game.players.all()
	player_colors = [player.color for player in players]
	return HttpResponse(json.dumps(player_colors), content_type='application/json', status=200)


def ImAliveGetAlive(request):
	player_code = request.POST.get('player_code', None)
	player = Player.objects.get(player_code=player_code)
	player.save()
	room_id = request.POST.get('room_id', None)
	game = Game.objects.get(room_id=room_id)
	if game.stage == -1:
		players = [player for player in game.players.all() if player.is_alive()]
	elif game.stage >= 0:
		players = game.players.all()
	player_colors = [player.color for player in players]
	return HttpResponse(json.dumps(player_colors), content_type='application/json', status=200)


def GameMoA(request):
	room_id = request.POST.get('room_id', None)
	if room_id is None:
		return redirect('MoA:SetupGame')

	game = Game.objects.get(room_id=room_id)
	if game.stage == -1:
		# game.stage = 0
		# To-Do: another ready check to set to 1
		game.stage = 101
		game.save()
		# all_colors = get_all_colors()
		# start_color = all_colors[game.start_color_index]
		# player = game.players.filter(color=color).first()
		player = game.players.all().first() # for testing
		player.sequence = 1
		player.save()
	player_code = request.session.get('player_code', None)
	me = Player.objects.get(player_code=player_code)
	players = game.players.all()
	return render(request, 'game.html', {'game': game, 'me': me, 'room_id': room_id, 'players': players})


def GetNextPlay(request):
	player_code = request.POST.get('player_code', None)
	room_id = request.POST.get('room_id', None)
	if player_code is None or room_id is None:
		return redirect('MoA:SetupGame')

	player = Player.objects.get(player_code=player_code)
	game = Game.objects.get(room_id=room_id)
	stage_round = int(game.stage / 100)
	if stage_round > 0 and player.sequence == game.stage % 10:
		start = stage_round - 1
		end = stage_round * 4
		# print(start, end)
		zodiacs = game.zodiacs.all()[start:end]
		ZODIACS = []
		for zodiac in zodiacs:
			ZODIACS.append({'pk': zodiac.pk, 'zodiac_image_url': zodiac.zodiac_image.image.url})
		# print(ZODIACS)
		return JsonResponse(ZODIACS, safe=False, status=201)
	elif player.sequence == game.stage % 100 / 10.0:
		return HttpResponse(serializers.serialize('json', game.players.all()), content_type='application/json', status=202)
	elif game.stage == 100:
		return HttpResponse('BB', status=203)
	else:
		return HttpResponse('wait', status=209)


def SetNextPlayer(request):
	player_code = request.POST.get('player_code', None)
	color = request.POST.get('color', None)
	if player_code is None or color is None:
		return redirect('MoA:SetupGame')

	cur_player = Player.objects.get(player_code=player_code)
	game = cur_player.game
	if cur_player.sequence == game.stage % 100 / 10.0:
		next_player = game.players.get(color=color)
		# print(next_player)
		next_player.sequence = cur_player.sequence + 1
		next_player.save()
		game.stage = game.stage - game.stage % 10 + next_player.sequence
		game.save()
	return HttpResponse()


def CheckGenuine(request):
	player_code = request.POST.get('player_code', None)
	room_id = request.POST.get('room_id', None)
	if player_code is None or room_id is None:
		return redirect('MoA:SetupGame')

	zodiac_pk = request.POST.get('zodiac_pk', None)
	if zodiac_pk is None:
		return redirect('MoA:GameMoA')

	player = Player.objects.get(player_code=player_code)
	game = Game.objects.get(room_id=room_id)
	zodiac = Zodiac.objects.get(pk=zodiac_pk)
	if player is None or game is None or zodiac is None:
		return redirect('MoA:GameMoA')

	if player.sequence != game.stage % 10:
		return redirect('MoA:GameMoA')

	game.stage = game.stage - game.stage % 100 + game.stage % 10 * 10
	game.save()
	return HttpResponse(zodiac.genuine, status=200)


def StartBB(request):
	room_id = request.POST.get('room_id', None)
	if room_id is None:
		return redirect('MoA:SetupGame')

	game = Game.objects.get(room_id=room_id)
	for player in game.players.all():
		if player.sequence > game.stage % 100 - game.stage % 10:
			return HttpResponse('not yet BB', status=209)
	game.stage = game.stage - game.stage % 100 + 99
	game.save()
	return HttpResponse('Start BB', status=200)


def EndGame(request):
	del request.session['player_code']
	# del request.session['join_at']
	# del request.session['create_at']
	return HttpResponse()


def TestGameMoA(request):
	room_id = request.POST.get('room_id', None)
	if room_id is None:
		return redirect('MoA:SetupGame')

	game = Game.objects.get(room_id=room_id)
	if game.stage == -1:
		# game.stage = 0
		# To-Do: another ready check to set to 1
		game.stage = 1
		game.save()
		all_colors = get_all_colors()
		start_color = all_colors[game.start_color_index]
		player = game.players.filter(color=color).first()
		player.sequence = 1
		player.save()
	player_code = request.session.get('player_code', None)
	me = Player.objects.get(player_code=player_code)
	return render(request, 'game.html', {'game': game, 'me': me, 'room_id': room_id})