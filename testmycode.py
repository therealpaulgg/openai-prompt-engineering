from sys import argv
import openai
import os
import argparse

parser = argparse.ArgumentParser(description='Test my code')
parser.add_argument('-f', '--file', help='File to test', required=True)
parser.add_argument('-o', '--output', help='Output file', required=True)
parser.add_argument('-li', '--log-input', help='Log input', required=False, default=False)
parser.add_argument('-c', '--context', help='Context', required=False, action="append", default=[])
parser.add_argument('-m', '--model', help='Model', required=False, default="gpt-3.5-turbo")

args = parser.parse_args()
file_path = args.file
output_file = args.output
log_input = args.log_input
context = args.context

file = open(file_path, "r")
file_data = file.read()
file.close()

data = "I have some code I would like to unit test.\n\n"
data += "```csharp\n" + file_data + "\n```\n"

data += "\n" + """
Please write some unit tests for this code. Requirements are:
- Tests must be written using the Xunit2 framework
- Tests must also use Moq for mocking services
- Tests make use of the [AutoMoqData] attribute which will automatically create test data
- Tests should use FluentAssertions instead of Assert.Equal, for example result.Succeeded().Should().BeTrue();
- Tests should use .Verifiable() at the end of ReturnsAsync() or ThrowsAsync()
- Use .Verify() and .VerifyNoOtherCalls() to verify that the mock was called
- Do not mock the Logger or Mapper services
- When returning null in a mock setup, use `() => null` instead of `null`

Here is an example of a stub for a successful unit test collection:
```csharp
public class HandlerTests
{
    [Theory, AutoMoqData]
    public async Task Handle_Success(
        [Frozen] Mock<IMyRepository> myRepository,
        MyEntity entity,
        MyRequest req,
        MyHandler uut)
    {
        // Arrange
        myRepository.Setup(x => x.GetSomethingAsync(req.Id)).ReturnsAsync(entity).Verifiable();
        // Act
        var result = await uut.Handle(req, CancellationToken.None);
        // Assert
        myRepository.Verify();
        myRepository.VerifyNoOtherCalls();
        result.Succeeded().Should().BeTrue();
    }

    [Theory, AutoMoqData]
    public async Task Handle_Failure(
        [Frozen] Mock<IMyRepository> myRepository,
        MyRequest req,
        MyHandler uut)
    {
        // Arrange
        myRepository.Setup(x => x.GetSomethingAsync(req.Id)).ThrowsAsync(new Exception("This did not work.")).Verifiable();
        // Act
        var result = await uut.Handle(req, CancellationToken.None);
        // Assert
        myRepository.Verify();
        myRepository.VerifyNoOtherCalls();
        result.Succeeded().Should().BeFalse();
        result.ErrorMessage.Should().Be("This did not work.");
    }
}
```
"""

if context:
    data += "\n" + "Here is additional context.\n\n"
    for c in context:
        data += c + "\n\n"
        context_file = open(c, "r")
        data += "```csharp\n" + context_file.read() + "\n```\n"

if log_input:
    input_file = open("input.md", "w")
    input_file.write(data)
    input_file.close()

openai.api_key = os.getenv("OPENAI_API_KEY")
response = openai.ChatCompletion.create(
    model=args.model,
    messages=[
        {"role": "user", "content": data}
    ],
    temperature=0.05,
)

print(response['choices'][0]['finish_reason'])

msg = response['choices'][0]['message']['content']
file = open(output_file, "w")
file.write(msg)
file.close()
