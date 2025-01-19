// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Lottery {
    address public manager; // Менеджер контракта
    address payable[] public players; // Массив участников
    uint256 public lotteryEndTime; // Время окончания лотереи
    uint256 public ticketPrice; // Стоимость билета

    event WinnerSelected(address winner, uint256 amount); // Событие для уведомления о победителе

    // Модификатор для проверки, что только менеджер может вызвать функцию
    modifier onlyManager() {
        require(msg.sender == manager, "Only manager can call this function");
        _;
    }

    // Конструктор для начальной настройки
    constructor(uint256 _durationMinutes, uint256 _ticketPrice) payable {
        manager = msg.sender; // Менеджер - адрес, который развернул контракт
        lotteryEndTime = block.timestamp + (_durationMinutes * 1 minutes); // Время окончания лотереи
        ticketPrice = _ticketPrice; // Устанавливаем стоимость билета
    }

    // Функция для участия в лотерее (payable)
    function participate() public payable {
        require(block.timestamp < lotteryEndTime, "Lottery has ended"); // Лотерея должна быть активной
        require(msg.value == ticketPrice, "Incorrect ticket price"); // Стоимость билета должна быть правильной

        players.push(payable(msg.sender)); // Добавляем адрес участника в массив
    }

    // Функция для получения количества участников (view)
    function getPlayersCount() public view returns (uint256) {
        return players.length; // Возвращаем количество участников
    }

    // Псевдослучайная функция для выбора победителя (использует block.timestamp, block.difficulty)
    function getRandomNumber() public view returns (uint256) {
        return uint256(keccak256(abi.encodePacked(block.timestamp, block.difficulty, players.length)));
    }

    // Функция для выбора победителя
    function selectWinner() public onlyManager {
        require(block.timestamp >= lotteryEndTime, "Lottery has not ended yet"); // Лотерея должна быть завершена
        require(players.length > 0, "No players in the lottery"); // Проверяем, есть ли участники

        uint256 randomNumber = getRandomNumber(); // Получаем случайное число
        uint256 winnerIndex = randomNumber % players.length; // Выбираем победителя

        address payable winner = players[winnerIndex]; // Получаем адрес победителя

        // Отправляем все собранные средства победителю
        winner.transfer(address(this).balance);

        emit WinnerSelected(winner, address(this).balance); // Событие для уведомления о победителе

        // Сбрасываем участников для следующей лотереи
        delete players;
        lotteryEndTime = block.timestamp + (30 * 1 minutes); // Новая лотерея через 30 минут
    }

    // Функция для получения баланса контракта (view)
    function getContractBalance() public view returns (uint256) {
        return address(this).balance;
    }
}
