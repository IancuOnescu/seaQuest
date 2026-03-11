import os

from seaquest.model_class import NautPipelineModel, OutputContext

class ExampleModel(NautPipelineModel):
    def __init__(self, output_dir, data_file, test_arg):
        super().__init__(output_dir, data_file)

        self.test_arg = test_arg

    def infer(self):
        with open('./test_weights.txt', 'r') as f:
            print("Loading weights from test_weights.txt")

        with OutputContext(self.output_dir):
            with open("delete_this.txt", "w") as f:
                f.write("Hello, this is a test!\n")
                f.write(self.test_arg)

            print("we are inside")
            print(os.getcwd())
        
        print("now we are back to")
        print(os.getcwd())

        print("this is the data dir")
        print(self.data_file)

    def train(self):
        with open('./test_weights.txt', 'r') as f:
            print("Loading weights from test_weights.txt")