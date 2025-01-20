async function main() {
  const { network } = require("hardhat");

  // На сколько секунд сдвигаем время (например, 1 час = 3600)
  const SECONDS = 3600;

  console.log(`Increasing time by ${SECONDS} seconds...`);
  // Увеличиваем время
  await network.provider.send("evm_increaseTime", [SECONDS]);
  // Майним новый блок, чтобы это сработало
  await network.provider.send("evm_mine");

  console.log("Time has been increased and a new block mined.");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
