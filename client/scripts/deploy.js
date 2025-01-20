const { ethers } = require("hardhat");

async function main() {
  // Получаем фабрику контракта
  const Lottery = await ethers.getContractFactory("Lottery");

  // Вызываем deploy(...) с параметрами конструктора (например, 1 и 10) в Hardhat:
  const lottery = await Lottery.deploy(1, 10, {
    value: ethers.parseEther("1") // 1 ETH
  });

  // Ждём, пока транзакция деплоя подтверждена
  await lottery.waitForDeployment();

  // Адрес контракта
  console.log("Lottery deployed to:", lottery.target);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
