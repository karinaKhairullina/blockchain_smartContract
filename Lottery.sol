// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Базовый контракт(общие функции для всех лотерей)
contract LotteryBase {
    address public manager;

    modifier onlyManager() {
        require(msg.sender == manager, "Only manager can call this function");
        _;
    }

    constructor() {
        manager = msg.sender;
    }

    // Метод view-отображает баланс контракта
    function getBalance() public view onlyManager returns(uint256) {
        return address(this).balance;
    }
}

// Лотерея, которая наследует функционал от LotteryBase
contract Lottery is LotteryBase {
    address payable[] public players;
    uint256 public lotteryEndTime;
    uint256 public ticketPrice;

    event WinnerSelected(address winner, uint256 amount);

    // Конструктор для начальной настройки
    constructor(uint256 _durationMinutes, uint256 _ticketPrice) {
        lotteryEndTime = block.timestamp + (_durationMinutes * 1 minutes);
        ticketPrice = _ticketPrice;
    }

    // Функция для участия в лотерее (payable)
    function participate() public payable {
        require(block.timestamp < lotteryEndTime, "Lottery has ended");
        require(msg.value == ticketPrice, "Incorrect ticket price");

        players.push(payable(msg.sender));  // Добавляем адрес участника в массив
    }

    // Функция для получения количества участников (view)
    function getPlayersCount() public view returns (uint256) {
        return players.length;
    }

    // Псевдослучайная функция для выбора победителя (использует block.timestamp, block.difficulty)
    function getRandomNumber() public view returns (uint256) {
        return uint256(keccak256(abi.encodePacked(block.timestamp, block.difficulty, players.length)));
    }

    // Функция для выбора победителя
    function selectWinner() public onlyManager {
        require(block.timestamp >= lotteryEndTime, "Lottery has not ended yet");
        require(players.length > 0, "No players in the lottery");

        uint256 randomNumber = getRandomNumber();
        uint256 winnerIndex = randomNumber % players.length;

        address payable winner = players[winnerIndex];

        // Отправляем все собранные средства победителю
        winner.transfer(address(this).balance);

        emit WinnerSelected(winner, address(this).balance);

        // Сбрасываем участников и сбрасываем время для новой лотереи
        players = new address payable      lotteryEndTime = block.timestamp + (30 * 1 minutes); // Новая лотерея через 30 минут
    }
}
