// Инициализация Telegram WebApp API
const tg = window.Telegram.WebApp;
tg.expand(); // Открываем на весь экран

// Состояние игрока
let player = {
    name: tg.initDataUnsafe?.user?.first_name || "Неизвестный Герой",
    level: 1,
    hp: 100,
    maxHp: 100,
    exp: 0,
    maxExp: 100,
    damage: 15
};

// Состояние врага
let enemy = {
    name: "Дикий Волк",
    hp: 50,
    maxHp: 50,
    damage: 8,
    expReward: 35
};

// Элементы DOM
const elPlayerName = document.getElementById('player-name');
const elPlayerLevel = document.getElementById('player-level');
const elHpText = document.getElementById('hp-text');
const elHpFill = document.getElementById('hp-fill');
const elExpText = document.getElementById('exp-text');
const elExpFill = document.getElementById('exp-fill');

const elEnemyName = document.getElementById('enemy-name');
const elEnemyHpText = document.getElementById('enemy-hp-text');
const elEnemyHpFill = document.getElementById('enemy-hp-fill');

const elCombatLog = document.getElementById('combat-log');
const btnAttack = document.getElementById('attack-btn');
const btnClose = document.getElementById('close-btn');

// Инициализация UI
function updateUI() {
    elPlayerName.innerText = player.name;
    elPlayerLevel.innerText = player.level;
    
    elHpText.innerText = `${player.hp}/${player.maxHp}`;
    elHpFill.style.width = `${(player.hp / player.maxHp) * 100}%`;
    
    elExpText.innerText = `${player.exp}/${player.maxExp}`;
    elExpFill.style.width = `${(player.exp / player.maxExp) * 100}%`;

    elEnemyName.innerText = enemy.name;
    elEnemyHpText.innerText = `${enemy.hp}/${enemy.maxHp}`;
    elEnemyHpFill.style.width = `${(enemy.hp / enemy.maxHp) * 100}%`;
}

function addLog(message) {
    const p = document.createElement('p');
    p.innerText = message;
    elCombatLog.appendChild(p);
    elCombatLog.scrollTop = elCombatLog.scrollHeight;
}

function spawnNewEnemy() {
    enemy.hp = enemy.maxHp;
    addLog(`Появляется новый ${enemy.name}!`);
    updateUI();
}

function levelUp() {
    player.level++;
    player.exp = player.exp - player.maxExp;
    player.maxExp = Math.floor(player.maxExp * 1.5);
    player.maxHp += 20;
    player.hp = player.maxHp; // Лечение при левелапе
    player.damage += 5;
    addLog(`🎉 Поздравляем! Вы достигли ${player.level} уровня!`);
}

// Логика боя
btnAttack.addEventListener('click', () => {
    if (player.hp <= 0) {
        addLog("Вы мертвы. Нажмите 'Выйти', чтобы начать заново.");
        return;
    }

    // Удар игрока
    enemy.hp -= player.damage;
    if (enemy.hp < 0) enemy.hp = 0;
    addLog(`Вы ударили ${enemy.name} на ${player.damage} урона.`);

    // Проверка смерти врага
    if (enemy.hp === 0) {
        addLog(`Вы убили ${enemy.name} и получили ${enemy.expReward} опыта.`);
        player.exp += enemy.expReward;
        
        if (player.exp >= player.maxExp) {
            levelUp();
        }
        
        updateUI();
        setTimeout(spawnNewEnemy, 1000);
        return;
    }

    // Удар врага
    player.hp -= enemy.damage;
    if (player.hp < 0) player.hp = 0;
    addLog(`${enemy.name} кусает вас на ${enemy.damage} урона.`);

    if (player.hp === 0) {
        addLog("💀 Вы погибли в бою...");
    }

    updateUI();
});

// Логика закрытия Web App
btnClose.addEventListener('click', () => {
    // Здесь позже можно отправлять данные о прогрессе обратно в бота через tg.sendData()
    tg.close();
});

// Старт
updateUI();
