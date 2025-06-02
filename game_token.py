from __future__ import annotations
from constants import *
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from character import UserPlayer, Enemy

class Token(ABC):
    """Tokens which influence game mechanics and spawn on the map.

    This is an abstract class and should not be instantiated.
    """
    def __init__(self, location: tuple[float, float], image: str) -> None:
        """Initialize a new Token at x, y coordinates contained in
        <location>.

        This is an abstract class and should not be instantiated.
        """
        self.x = location[0]
        self.y = location[1]
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw <self> on <screen>."""
        screen.blit(self.image, self.rect)

    @abstractmethod
    def collect(self, player: UserPlayer, tokens: list[Token]) -> None:
        raise NotImplementedError


class ScoreToken(Token):
    """Tokens which increase UserPlayer's score when collected."""
    def __init__(self, location: tuple[float, float]) -> None:
        """Initialize a new AmmoToken at x, y coordinates contained in
        <location>.
        """
        super().__init__(location, "assets/token_icons/score_icon.png")

    def collect(self, player: UserPlayer, tokens: list[Token]) -> None:
        """Increase <player>'s score by 100 and remove <self> from <tokens> if
        <player> collides with <self>.
        """
        if self.rect.collidepoint(player.rect.center):
            player.add_score(100)
            tokens.remove(self)


class AmmoToken(Token):
    """Tokens which increase UserPlayer's ammo when collected."""
    def __init__(self, location: tuple[float, float]) -> None:
        """Initialize a new AmmoToken at x, y coordinates contained in
        <location>.
        """
        super().__init__(location, "assets/token_icons/ammo_icon.png")

    def collect(self, player: UserPlayer, tokens: list[Token]) -> None:
        """Increase <player>'s ammo by 5 and remove <self> from <tokens> if
        <player> collides with <self>.
        """
        if self.rect.collidepoint(player.rect.center):
            player.add_ammo(5)
            tokens.remove(self)


class PowerUpToken(Token, ABC):
    """Tokens for power-ups lasting 30 seconds.

    This is an abstract class and should not be instantiated.
    """
    def __init__(self, location: tuple[float, float]) -> None:
        """Initialize a new PowerUpToken at x, y coordinates contained in
        <location>. start_time is set to None until UserPlayer collects <self>.

        This is an abstract class and should not be instantiated.
        """
        super().__init__(location, "assets/token_icons/powerup_icon.png")
        self.start_time = None

    def collect(self, player: UserPlayer, tokens: list[Token]) -> None:
        """If <player> is not currently using a power-up and <player> collides
        with <self>, set <player>'s power-up to <self>, set <self>'s start_time
        to the time of collision and remove <self> from <tokens>.
        """
        if player.power_up is not None:
            return None
        if self.rect.collidepoint(player.rect.center):
            self.start_time = pygame.time.get_ticks()
            tokens.remove(self)
            player.set_power_up(self)

    def check_for_completion(self) -> bool:
        """Return true if <self> has been active for more than 30 seconds.
        This represents that <self> has ended.
        """
        if pygame.time.get_ticks() - self.start_time >= 30_000:
            return True
        return False

    @abstractmethod
    def __str__(self) -> str:
        """Return a str representation of <self> used for comparisons in the
        UserPlayer class.
        """
        raise NotImplementedError


class PUSDoubleShootingSpeed(PowerUpToken):
    """Power-up which doubles UserPlayer's shooting speed."""
    def __str__(self) -> str:
        """Return a str representation of <self> used for comparisons in the
        UserPlayer class.
        """
        return "DoubleShootingSpeed"


class PUDoubleMovementSpeed(PowerUpToken):
    """Power-up which doubles UserPlayer's movement speed."""
    def __str__(self) -> str:
        """Return a str representation of <self> used for comparisons in the
        UserPlayer class.
        """
        return "DoubleMovementSpeed"


class PUDoubleScore(PowerUpToken):
    """Power-up which doubles UserPlayer's score per action."""
    def __str__(self) -> str:
        """Return a str representation of <self> used for comparisons in the
        UserPlayer class.
        """
        return "DoubleScore"


class PUPiercingAmmo(PowerUpToken):
    """Power-up which allows UserPlayer's ammo to pierce through multiple
    enemies."""
    def __str__(self) -> str:
        """Return a str representation of <self> used for comparisons in the
        UserPlayer class.
        """
        return "PiercingAmmo"


class Bullet:
    """Death-inflicting projectiles launched by UserPlayer."""
    def __init__(self, x: float, y: float, direction: str) -> None:
        """Initialize a Bullet at <x>, <y> with direction <direction>."""
        self.x = x
        self.y = y
        self.rect = pygame.Rect(int(x - 2), int(y - 2), 4, 4)
        self.direction = direction

    def place(self, screen: pygame.Surface) -> None:
        """Update <self>'s position and draws <self> on <screen>."""
        self.update()
        self.draw(screen)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw <self> on <screen>."""
        pygame.draw.circle(screen, "white", (self.x, self.y), 3)

    def update(self) -> None:
        """Move <self> to its new position based on its direction and speed."""
        self.x += MOVEMENT_COEFFICIENTS[self.direction][0] * BULLET_SPEED
        self.y += MOVEMENT_COEFFICIENTS[self.direction][1] * BULLET_SPEED

    def check_for_enemies(self, enemies: list[Enemy]) -> int:
        """Return the number of enemies hit by <self> and remove them from
        <enemies>.
        """
        kills = 0
        for enemy in enemies.copy():
            if enemy.rect.collidepoint((self.x, self.y)):
                enemies.remove(enemy)
                kills += 1
        return kills
