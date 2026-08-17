
import data_fetcher # module where you got your custom logic



# HERE YOU WILL DEFINE STUFF


if __name__ == '__main__': # separator between definitions and functional code
    my_data = data_fetcher.fetch_ohlcv("MSFT")

    #data_fetcher.save_to_csv(my_data, "./data/my_data.csv")
    ... # YOUR CODE WILL RUN HERE