import hnq_settings as settings

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    settings.screen.blit(img, (x, y))

def draw_bg():
    settings.screen.fill(settings.BG)
    width = settings.sky_img.get_width()
    for x in range(5):
        settings.screen.blit(settings.sky_img, ((x * width) - settings.bg_scroll * 0.5, 0))
        settings.screen.blit(settings.mountain_img, ((x * width) - settings.bg_scroll * 0.6, settings.SCREEN_HEIGHT - settings.mountain_img.get_height() - 300))
        settings.screen.blit(settings.pine1_img, ((x * width) - settings.bg_scroll * 0.7, settings.SCREEN_HEIGHT - settings.pine1_img.get_height() - 150))
        settings.screen.blit(settings.pine2_img, ((x * width) - settings.bg_scroll * 0.8, settings.SCREEN_HEIGHT - settings.pine2_img.get_height()))


def reset_level():
    settings.enemy_group.empty()
    settings.bullet_group.empty()
    settings.grenade_group.empty()
    settings.explosion_group.empty()
    settings.item_box_group.empty()
    settings.decoration_group.empty()
    settings.water_group.empty()
    settings.exit_group.empty()

    data = []
    for row in range(settings.ROWS):
        r = [-1] * settings.COLS
        data.append(r)
    return data
